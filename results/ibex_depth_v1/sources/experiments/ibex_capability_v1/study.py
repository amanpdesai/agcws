"""One next batch per common context; no response repair or on-policy feedback."""

import argparse
import concurrent.futures
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
from experiments.ibex_temporal_v3.coverage import BehaviorArchive
from experiments.ibex_temporal_v3.program import canonical, random_program
from experiments.ibex_temporal_v3.search import error, verify_runtime
from experiments.ibex_temporal_v4.cache import measured
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.native_schema import serving_schema
from experiments.ibex_temporal_v4.notebook import assess
from experiments.ibex_temporal_v4.transport import client, request

PREVIOUS = Path("results/ibex_temporal_v4_development")
BINARY = Path(
    "toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system"
)
MODEL_ARMS = ("flash-512", "flash-4096", "pro-512", "pro-4096")
ARMS = (*MODEL_ARMS, "random", "coverage")


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write("\n")


def settings(arm):
    tier, budget = arm.split("-")
    return {
        "model": f"gemini-2.5-{tier}",
        "thinking_budget": int(budget),
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 16384,
        "input_rate": 0.3 if tier == "flash" else 1.25,
        "output_rate": 2.5 if tier == "flash" else 10.0,
    }


def estimate(info, arm):
    s = settings(arm)
    if info["tokens_in"] > 200000 and arm.startswith("pro"):
        s.update(input_rate=2.5, output_rate=15.0)
    return (
        info["tokens_in"] * s["input_rate"] + info["tokens_out"] * s["output_rate"]
    ) / 1e6


def controls(arm, history, seed):
    rng = random.Random(seed)
    if arm == "random":
        return [random_program(rng) for _ in range(2)]
    archive = BehaviorArchive()
    for trial in history:
        archive.observe(trial)
    return [archive.propose(rng)[0] for _ in range(2)]


def summarize_slots(history, trials, tolerance):
    before = min(t["loss"] for t in history if t["valid"])
    after = min([before, *[t["loss"] for t in trials if t["valid"]]])
    return {
        "before_error": before,
        "after_error": after,
        "gain": before - after,
        "improved": after < before,
        "already_solved": before <= tolerance,
        "newly_solved": before > tolerance and after <= tolerance,
        "valid_slots": sum(t["valid"] for t in trials),
        "requested_slots": 2,
    }


def freeze(root, destination):
    from analysis.ibex_temporal_v4 import verify as verify_previous

    verify_previous(PREVIOUS)
    old = read(PREVIOUS / "manifest.json")
    root.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    source_binary = Path("out/ibex-temporal-v4") / BINARY
    os.link(source_binary, root / BINARY)
    verify_runtime(old, root)
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "previous_manifest.json", old)
    write(destination / "schema.json", serving_schema(2, True))
    contexts, cells = {}, []
    for index, (target, seed) in enumerate(
        (t, s) for t in old["targets"] for s in old["seeds"]
    ):
        name = f"{target}-{seed}"
        history_path = (
            PREVIOUS / "panel" / target / f"seed-{seed}" / "agent-base/trials.jsonl"
        )
        history = [json.loads(l) for l in history_path.read_text().splitlines()][:6]
        if len(history) != 6 or not any(t["valid"] for t in history):
            raise ValueError("incomplete historical context")
        write(destination / "contexts" / f"{name}.json", history)
        contents = payload(
            history,
            {
                "profile": old["targets"][target]["rates"],
                "scale": old["scale"],
                "tolerance": old["tolerance"],
            },
            2,
            True,
        )
        p = destination / "payloads" / f"{name}.json"
        p.parent.mkdir(exist_ok=True)
        with p.open("x") as f:
            f.write(contents + "\n")
        if (
            len(contents.encode()) + (destination / "schema.json").stat().st_size + 4096
            > 200000
        ):
            raise ValueError("payload exceeds conservative short-context allowance")
        contexts[name] = {
            "target": target,
            "seed": seed,
            "parent_history_sha256": file_sha256(history_path),
            "history_sha256": file_sha256(destination / "contexts" / f"{name}.json"),
            "payload_sha256": file_sha256(p),
        }
        rotated = MODEL_ARMS[index % 4 :] + MODEL_ARMS[: index % 4]
        for arm in (*rotated, "random", "coverage"):
            cells.append(
                {
                    "context": name,
                    "arm": arm,
                    "seed": 17000 + index * 100 + ARMS.index(arm),
                }
            )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    files = (
        set(old["sources"])
        | {str(p) for p in Path("experiments/ibex_capability_v1").glob("*.py")}
        | {"docs/IBEX_CAPABILITY_V1_PROTOCOL.md"}
    )
    sources = {}
    for name in sorted(files):
        data = subprocess.check_output(["git", "show", f"{commit}:{name}"])
        if hashlib.sha256(data).hexdigest() != file_sha256(Path(name)):
            raise ValueError(f"source not committed: {name}")
        sources[name] = file_sha256(Path(name))
        target = destination / "sources" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    arms = {a: settings(a) for a in MODEL_ARMS}
    reservation = sum(
        (200000 * s["input_rate"] + s["max_output_tokens"] * s["output_rate"]) / 1e6
        for s in arms.values()
    ) * len(contexts)
    if reservation > 20:
        raise ValueError("conservative model reservation exceeds $20")
    write(
        destination / "manifest.json",
        {
            "phase": "fixed-context-development",
            "source_commit": commit,
            "sources": sources,
            "previous_manifest_sha256": file_sha256(PREVIOUS / "manifest.json"),
            "schema_sha256": file_sha256(destination / "schema.json"),
            "contexts": contexts,
            "cells": cells,
            "arms": arms,
            "measurement_fingerprint": old["measurement_fingerprint"],
            "reservation_usd": reservation,
            "ceiling_usd": 20,
            "requested_slots_per_cell": 2,
            "api_attempts": 1,
            "max_workers": 4,
        },
    )


def verify_inputs(destination, root):
    manifest = read(destination / "manifest.json")
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"frozen source changed: {name}")
    old = read(destination / "previous_manifest.json")
    if (
        file_sha256(destination / "previous_manifest.json")
        != manifest["previous_manifest_sha256"]
    ):
        raise ValueError("prior manifest changed")
    verify_runtime(old, root)
    for name, c in manifest["contexts"].items():
        for folder, key in (
            ("contexts", "history_sha256"),
            ("payloads", "payload_sha256"),
        ):
            if file_sha256(destination / folder / f"{name}.json") != c[key]:
                raise ValueError("frozen context changed")
    if file_sha256(destination / "schema.json") != manifest["schema_sha256"]:
        raise ValueError("frozen schema changed")
    committed = subprocess.check_output(
        ["git", "show", f"HEAD:{destination / 'manifest.json'}"]
    )
    if hashlib.sha256(committed).hexdigest() != file_sha256(
        destination / "manifest.json"
    ):
        raise ValueError("commit manifest before requests")
    return manifest, old


def generate(cell, destination, root, manifest, api_lock):
    directory = root / "cells" / cell["context"] / cell["arm"]
    directory.mkdir(parents=True, exist_ok=True)
    response = directory / "response.json"
    if response.exists():
        data = read(response)
        if data["manifest_sha256"] != file_sha256(destination / "manifest.json"):
            raise ValueError("response belongs to another manifest")
        return data
    write(
        directory / "request_started.json",
        {"manifest_sha256": file_sha256(destination / "manifest.json"), "cell": cell},
    )
    history = read(destination / "contexts" / f"{cell['context']}.json")
    arm = cell["arm"]
    if arm in MODEL_ARMS:
        with api_lock:
            started = time.monotonic()
            try:
                info = request(
                    client(os.environ["AGCWS_GCP_PROJECT"]),
                    manifest["arms"][arm]["model"],
                    (destination / "payloads" / f"{cell['context']}.json")
                    .read_text()
                    .rstrip("\n"),
                    manifest["arms"][arm],
                    read(destination / "schema.json"),
                )
            except Exception as exc:
                info = {
                    "raw_text": "",
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "est_cost_usd": 0.0,
                    "usage_unknown": True,
                    "exception": type(exc).__name__,
                    "message": str(exc),
                }
            info["request_wall_clock_s"] = time.monotonic() - started
        info["est_cost_usd"] = estimate(info, arm)
        info["long_context_tier"] = info["tokens_in"] > 200000
    else:
        info = {
            "raw_text": json.dumps(
                {
                    "hypothesis": "CPU control",
                    "candidates": controls(arm, history, cell["seed"]),
                }
            ),
            "tokens_in": 0,
            "tokens_out": 0,
            "est_cost_usd": 0.0,
            "usage_unknown": False,
        }
    info.update(cell=cell, manifest_sha256=file_sha256(destination / "manifest.json"))
    info["decoded"] = decode(info["raw_text"], 2, arm in MODEL_ARMS)
    write(response, info)
    return info


def evaluate_cell(cell, destination, root, manifest, old, api_lock):
    directory = root / "cells" / cell["context"] / cell["arm"]
    if (directory / "result.json").exists():
        return read(directory / "result.json")
    info = generate(cell, destination, root, manifest, api_lock)
    history = read(destination / "contexts" / f"{cell['context']}.json")
    target = old["targets"][manifest["contexts"][cell["context"]]["target"]]["rates"]
    trials = []
    for index, proposal in enumerate(info["decoded"]["slots"], 7):
        record, hit = measured(
            proposal["submitted"], root, manifest["measurement_fingerprint"]
        )
        rates = record["profile"]["window_rates"] if record["valid"] else None
        trial = {
            "slot": index,
            "program": proposal["submitted"],
            "canonical_program": canonical(proposal["submitted"])
            if record.get("cache_id")
            else None,
            "prediction": proposal["prediction"],
            "prediction_error": proposal["prediction_error"],
            "rates": rates,
            "loss": error(rates, target, old["scale"]) if rates is not None else None,
            "cache_hit": hit,
            **{
                k: record.get(k)
                for k in (
                    "valid",
                    "stage",
                    "reason",
                    "schema_path",
                    "cache_id",
                    "feedback",
                    "execution",
                )
            },
        }
        if trial["prediction"] and trial["prediction"]["reference_slot"] not in {
            t["slot"] for t in history if t["valid"]
        }:
            trial["prediction_error"] = (
                "reference was not visible as valid before this batch"
            )
        trial["prediction_assessment"] = assess(trial, history, old["scale"])
        trials.append(trial)
    result = {
        "cell": cell,
        "trials": trials,
        "summary": summarize_slots(history, trials, old["tolerance"]),
    }
    write(directory / "result.json", result)
    print(json.dumps({"cell": cell, "complete": True}), flush=True)
    return result


def run(root, destination, workers):
    manifest, old = verify_inputs(destination, root)
    if not 1 <= workers <= manifest["max_workers"]:
        raise ValueError("worker count outside frozen limits")
    config._load_dotenv()
    lock = threading.Lock()
    gate = [
        generate(c, destination, root, manifest, lock) for c in manifest["cells"][:4]
    ]
    ready = all(not r["usage_unknown"] and "exception" not in r for r in gate)
    status = root / "endpoint_gate.json"
    if not status.exists():
        write(
            status,
            {
                "ready": ready,
                "response_paths": [
                    f"cells/{r['cell']['context']}/{r['cell']['arm']}/response.json"
                    for r in gate
                ],
            },
        )
    if not ready:
        raise RuntimeError(
            "endpoint/settings acceptance failed; no remaining requests issued"
        )
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(evaluate_cell, c, destination, root, manifest, old, lock)
            for c in manifest["cells"]
        ]
        for f in concurrent.futures.as_completed(futures):
            f.result()
    if not (root / "panel_complete.json").exists():
        write(
            root / "panel_complete.json",
            {"cells": len(manifest["cells"]), "slots": 2 * len(manifest["cells"])},
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
