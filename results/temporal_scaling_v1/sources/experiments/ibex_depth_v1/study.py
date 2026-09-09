"""Stage-wide prefix execution with immutable per-batch checkpoints."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
import random
import subprocess
import threading
import time
from pathlib import Path

from agcws import config
from agcws.provenance import file_sha256
from experiments.ibex_capability_v1.study import BINARY
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.model import ARMS, MODELS, cost, generate, settings
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_temporal_v3.coverage import BehaviorArchive
from experiments.ibex_temporal_v3.program import canonical, random_program
from experiments.ibex_temporal_v3.search import error, verify_runtime
from experiments.ibex_temporal_v4.cache import measured
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.native_schema import serving_schema
from experiments.ibex_temporal_v4.notebook import assess

PARENT = Path("results/ibex_temporal_v4_development/manifest.json")
PREFIXES = (16, 64, 128)
SEEDS = (610, 611, 612)


def freeze(root, destination):
    old = read(PARENT)
    root.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    os.link(Path("out/ibex-temporal-v4") / BINARY, root / BINARY)
    verify_runtime(old, root)
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "parent_manifest.json", old)
    write(destination / "schema.json", serving_schema(2, True))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    names = (
        set(old["sources"])
        | {str(p) for p in Path("experiments/ibex_depth_v1").glob("*.py")}
        | {"docs/IBEX_DEPTH_V1_PROTOCOL.md", "experiments/ibex_capability_v1/study.py"}
    )
    sources = {}
    for name in sorted(names):
        data = subprocess.check_output(["git", "show", f"{commit}:{name}"])
        digest = hashlib.sha256(data).hexdigest()
        if digest != file_sha256(Path(name)):
            raise ValueError(f"uncommitted source: {name}")
        sources[name] = digest
        p = destination / "sources" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    write(
        destination / "manifest.json",
        {
            "phase": "closed-loop-depth-development",
            "source_commit": commit,
            "sources": sources,
            "parent_sha256": file_sha256(PARENT),
            "schema_sha256": file_sha256(destination / "schema.json"),
            "measurement_fingerprint": old["measurement_fingerprint"],
            "targets": old["targets"],
            "scale": old["scale"],
            "tolerance": old["tolerance"],
            "seeds": list(SEEDS),
            "prefixes": list(PREFIXES),
            "arms": list(ARMS),
            "models": {arm: settings(arm) for arm in MODELS},
            "cells": [
                {"target": target, "seed": seed, "arm": arm}
                for target in old["targets"]
                for seed in SEEDS
                for arm in ARMS
            ],
            "batch_size": 2,
            "initial_slots": 2,
            "max_workers": 4,
            "ceiling_usd": 180,
            "payload_bound": 200000,
        },
    )


def verify_inputs(root, destination):
    manifest = read(destination / "manifest.json")
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"frozen source changed: {name}")
    old = read(destination / "parent_manifest.json")
    if file_sha256(destination / "parent_manifest.json") != manifest["parent_sha256"]:
        raise ValueError("parent manifest changed")
    verify_runtime(old, root)
    for arm in MODELS:
        if settings(arm) != manifest["models"][arm]:
            raise ValueError("model settings changed")
    if file_sha256(destination / "schema.json") != manifest["schema_sha256"]:
        raise ValueError("response schema changed")
    path = destination / "manifest.json"
    data = subprocess.check_output(["git", "show", f"HEAD:{path}"])
    if hashlib.sha256(data).hexdigest() != file_sha256(path):
        raise ValueError("commit manifest before execution")
    return manifest


class Meter:
    def __init__(self, root, ceiling):
        self.lock = threading.Lock()
        self.halted = threading.Event()
        self.ceiling = ceiling
        self.liability = 0.0
        for p in root.glob("panel/*/*/*/batches/*/request_started.json"):
            started = read(p)
            response = p.parent / "response.json"
            info = read(response) if response.exists() else None
            self.liability += (
                info["estimated_usd"]
                if info and not info["usage_unknown"]
                else started["reservation_usd"]
            )

    def call(self, directory, arm, contents, schema, identity):
        from google.genai.errors import APIError
        from httpx import TransportError

        response = directory / "response.json"
        if response.exists():
            info = read(response)
            if info["identity"] != identity:
                raise ValueError("saved response identity differs")
            return info
        with self.lock:
            if self.halted.is_set():
                raise RuntimeError("stage halted after an infrastructure failure")
            marker = directory / "request_started.json"
            if marker.exists():
                raise RuntimeError(f"unresolved request, refusing resample: {marker}")
            reservation = cost(arm, 200000, settings(arm)["max_output_tokens"])
            if self.liability + reservation > self.ceiling:
                raise RuntimeError(
                    "study cost ceiling reached; no replacement or extra call"
                )
            write(
                marker,
                {
                    "identity": identity,
                    "reservation_usd": reservation,
                    "started_unix": time.time(),
                },
            )
            self.liability += reservation
            started = time.monotonic()
            try:
                info = generate(os.environ["AGCWS_GCP_PROJECT"], arm, contents, schema)
            except (APIError, TransportError) as exc:
                info = {
                    "raw_text": "",
                    "tokens_in": None,
                    "tokens_out": None,
                    "thinking_tokens": None,
                    "estimated_usd": None,
                    "usage_unknown": True,
                    "model_version": None,
                    "finish_reasons": [],
                    "prompt_feedback": None,
                    "api_error": {"type": type(exc).__name__, "message": str(exc)},
                }
            info.update(
                identity=identity, request_wall_clock_s=time.monotonic() - started
            )
            write(response, info)
            if not info["usage_unknown"]:
                self.liability += info["estimated_usd"] - reservation
            return info


def controls(arm, rng, archive):
    if arm == "random":
        return [random_program(rng) for _ in range(2)]
    if arm == "coverage":
        return [archive.propose(rng)[0] for _ in range(2)]
    raise ValueError(f"not a CPU control: {arm}")


def evaluate(proposal, slot, history, manifest, root, mode):
    result, hit = measured(
        proposal["submitted"], root, manifest["measurement_fingerprint"]
    )
    rates = result["profile"]["window_rates"] if result["valid"] else None
    note, note_error = proposal["prediction"], proposal["prediction_error"]
    if note and note["reference_slot"] not in {
        t["slot"] for t in history if t["valid"]
    }:
        note_error = "reference was not visible as valid before this batch"
    trial = {
        "slot": slot,
        "program": proposal["submitted"],
        "canonical_program": canonical(proposal["submitted"])
        if result.get("cache_id")
        else None,
        **{
            k: result.get(k)
            for k in (
                "valid",
                "stage",
                "reason",
                "schema_path",
                "allocation",
                "cache_id",
                "feedback",
                "execution",
            )
        },
        "rates": rates,
        "loss": error(rates, manifest["target_rates"], manifest["scale"])
        if rates is not None
        else None,
        "residual": [
            (a - b) / manifest["scale"] for a, b in zip(rates, manifest["target_rates"])
        ]
        if rates
        else None,
        "prediction": note,
        "prediction_error": note_error,
        "proposal_mode": mode,
        "cache_hit": hit,
        "evaluation_s": result.get("evaluation_s"),
    }
    trial["prediction_assessment"] = assess(trial, history, manifest["scale"])
    return trial


def search(cell, budget, root, destination, manifest, meter):
    target, seed, arm = cell["target"], cell["seed"], cell["arm"]
    if cell not in manifest["cells"] or budget not in manifest["prefixes"]:
        raise ValueError("cell or prefix outside manifest")
    directory = root / "panel" / target / str(seed) / arm
    digest = file_sha256(destination / "manifest.json")
    ensure(directory / "identity.json", {"cell": cell, "manifest_sha256": digest})
    rng, archive = random.Random(seed), BehaviorArchive()
    history = []
    local = {**manifest, "target_rates": manifest["targets"][target]["rates"]}
    for offset in range(0, budget, 2):
        if meter.halted.is_set():
            raise RuntimeError("stage halted; checkpoints retained")
        batch_dir = directory / "batches" / f"{offset + 1:03d}"
        model_batch = arm in MODELS and offset > 0
        candidates = None
        if offset == 0:
            candidates = [random_program(rng) for _ in range(2)]
        elif not model_batch:
            candidates = controls(arm, rng, archive)
        contents = (
            payload(
                history,
                {
                    "profile": local["target_rates"],
                    "scale": manifest["scale"],
                    "tolerance": manifest["tolerance"],
                },
                2,
                True,
            )
            if model_batch
            else None
        )
        identity = {"cell": cell, "first_slot": offset + 1, "manifest_sha256": digest}
        ensure(
            batch_dir / "input.json",
            {
                "identity": identity,
                "payload": contents,
                "cpu_candidates": candidates,
            },
        )
        if model_batch:
            schema = read(destination / "schema.json")
            if (
                len(contents.encode()) + len(json.dumps(schema).encode()) + 4096
                > manifest["payload_bound"]
            ):
                raise RuntimeError(
                    "payload exceeds frozen input bound; no silent truncation"
                )
            response = meter.call(batch_dir, arm, contents, schema, identity)
            if (
                not response.get("api_error")
                and response["model_version"] != manifest["models"][arm]["model"]
            ):
                raise RuntimeError(
                    "model identity changed; response retained, stage halted"
                )
            decoded = decode(response["raw_text"], 2, True)
        else:
            decoded = decode(
                json.dumps({"hypothesis": "CPU proposal", "candidates": candidates}), 2
            )
        ensure(batch_dir / "decoded.json", decoded)
        if (batch_dir / "trials.json").exists():
            trials = read(batch_dir / "trials.json")
            if len(trials) != 2 or any(
                t["slot"] != offset + j + 1
                or t["program"] != decoded["slots"][j]["submitted"]
                for j, t in enumerate(trials)
            ):
                raise ValueError("saved batch differs from submitted proposals")
        else:
            trials = [
                evaluate(
                    p,
                    offset + j + 1,
                    history,
                    local,
                    root,
                    "initial" if offset == 0 else arm,
                )
                for j, p in enumerate(decoded["slots"])
            ]
            if model_batch and response.get("api_error"):
                for trial in trials:
                    trial.update(stage="API", reason=response["api_error"]["message"])
            write(batch_dir / "trials.json", trials)
        for t in trials:
            archive.observe(t)
        history.extend(trials)
    summary = summarize(history, budget, manifest["tolerance"])
    ensure(directory / f"prefix-{budget}.json", {"cell": cell, **summary})
    print(
        json.dumps(
            {
                "cell": cell,
                "prefix": budget,
                "auc": summary["auc"],
                "solved": summary["solved"],
            }
        ),
        flush=True,
    )
    return summary


def run(root, destination, workers):
    root.mkdir(parents=True, exist_ok=True)
    with (root / "runner.lock").open("a") as guard:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = verify_inputs(root, destination)
        if not 1 <= workers <= manifest["max_workers"]:
            raise ValueError("worker count outside frozen limits")
        config._load_dotenv()
        meter = Meter(root, manifest["ceiling_usd"])
        for budget in manifest["prefixes"]:
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [
                    pool.submit(search, c, budget, root, destination, manifest, meter)
                    for c in manifest["cells"]
                ]
                try:
                    for future in concurrent.futures.as_completed(futures):
                        future.result()
                except Exception:
                    meter.halted.set()
                    for future in futures:
                        future.cancel()
                    raise
            ensure(
                root / f"prefix-{budget}-complete.json",
                {
                    "cells": len(manifest["cells"]),
                    "slots": len(manifest["cells"]) * budget,
                    "manifest_sha256": file_sha256(destination / "manifest.json"),
                },
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.archive)
    else:
        run(args.root, args.archive, args.workers)
