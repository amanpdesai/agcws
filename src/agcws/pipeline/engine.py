"""The single active study loop: proposals, measurements, checkpoints, summaries."""

import concurrent.futures
import fcntl
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from agcws.pipeline.ibex.domain import evaluate
from agcws.pipeline.ibex.native_schema import serving_schema
from agcws.pipeline.meter import Meter
from agcws.pipeline.metrics import key, summarize
from agcws.pipeline.model import MODELS, settings
from agcws.pipeline.policies.dispatch import Policy
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import ensure, read, write
from agcws.provenance import file_sha256

BINARY = Path("toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system")


def source_inventory(repo):
    roots = (
        repo / "src/agcws",
        repo / "third_party/ibex/examples/sw/simple_system/common",
    )
    paths = [
        p for root in roots for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts
    ]
    paths = [p for p in paths if p.suffix in (".py", ".S", ".c", ".h", ".ld")]
    paths.append(repo / "docker/run.sh")
    return {str(p.relative_to(repo)): file_sha256(p) for p in sorted(paths)}


def prepare(repo, spec_path, root):
    spec = validate(read(spec_path))
    binary = Path(spec["binary"]).expanduser().resolve(strict=True)
    image = subprocess.check_output(
        ["docker", "image", "inspect", spec["image"], "--format", "{{.Id}}"], text=True
    ).strip()
    sources = source_inventory(repo)
    runtime = {"image_id": image, "binary_sha256": file_sha256(binary)}
    manifest = {
        "version": 1,
        "spec": spec,
        "sources": sources,
        "runtime": runtime,
        "models": {a: settings(a) for a in spec["policies"] if a in MODELS},
        "measurement_fingerprint": key(
            {"sources": sources, "runtime": runtime, "domain": spec["domain"]}
        ),
        "schema": serving_schema(spec["batch_size"], True),
    }
    root.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    shutil.copy2(binary, root / BINARY)
    write(root / "manifest.json", manifest)
    return manifest


def verify_inputs(repo, root):
    m = read(root / "manifest.json")
    validate(m["spec"])
    if source_inventory(repo) != m["sources"]:
        raise ValueError("prepared source inventory changed")
    if m["measurement_fingerprint"] != key(
        {
            "sources": m["sources"],
            "runtime": m["runtime"],
            "domain": m["spec"]["domain"],
        }
    ):
        raise ValueError("measurement fingerprint differs")
    if m["schema"] != serving_schema(m["spec"]["batch_size"], True):
        raise ValueError("prepared response schema differs")
    if file_sha256(root / BINARY) != m["runtime"]["binary_sha256"]:
        raise ValueError("simulator changed")
    image = subprocess.check_output(
        ["docker", "image", "inspect", m["runtime"]["image_id"], "--format", "{{.Id}}"],
        text=True,
    ).strip()
    if image != m["runtime"]["image_id"]:
        raise ValueError("container identity changed")
    if m["models"] != {a: settings(a) for a in m["spec"]["policies"] if a in MODELS}:
        raise ValueError("model settings changed")
    return m


def cell(root, manifest, target, seed, arm, meter, evaluator=evaluate):
    spec = manifest["spec"]
    directory = root / "panel" / target / str(seed) / arm
    ident = {
        "target": target,
        "seed": seed,
        "arm": arm,
        "manifest_sha256": file_sha256(root / "manifest.json"),
    }
    ensure(directory / "identity.json", ident)
    policy = Policy(arm, seed, spec, spec["targets"][target], manifest["schema"], meter)
    history = []
    while len(history) < spec["budget"]:
        if meter.halted.is_set():
            raise RuntimeError("study halted; checkpoint retained")
        offset = len(history)
        batch = directory / "batches" / f"{offset + 1:03}"
        request = policy.propose(history, batch, {**ident, "first_slot": offset + 1})
        if not request or len(request) > spec["budget"] - offset:
            raise ValueError("empty or over-budget proposal batch")
        if [p["slot"] for p in request] != list(range(offset + 1, offset + len(request) + 1)):
            raise ValueError("noncontiguous proposal slots")
        ensure(batch / "proposals.json", request)
        if (batch / "trials.json").exists():
            trials = read(batch / "trials.json")
            if len(trials) != len(request) or any(
                any(t.get(k) != v for k, v in p.items())
                for t, p in zip(trials, request, strict=True)
            ):
                raise ValueError("saved trial/proposal mismatch")
        else:
            trials = []
            for proposal in request:
                if not proposal["selected"]:
                    trial = {
                        "valid": None,
                        "loss": None,
                        "rates": None,
                        "status": "FILTERED",
                    }
                else:
                    trial = evaluator(
                        {
                            "submitted": proposal["program"],
                            "prediction": proposal.get("prediction"),
                            "prediction_error": proposal.get("prediction_error"),
                        },
                        proposal["slot"],
                        history,
                        {
                            **manifest,
                            "scale": spec["scale"],
                            "target_rates": spec["targets"][target],
                        },
                        root,
                        arm,
                    )
                    trial["status"] = "MEASURED"
                    if proposal.get("api_error"):
                        trial.update(stage="API", reason=proposal["api_error"]["message"])
                    if trial["valid"] is not True and trial["loss"] is not None:
                        raise ValueError("invalid workload received a score")
                trial.update(proposal)
                trials.append(trial)
            write(batch / "trials.json", trials)
        policy.observe(trials)
        history.extend(trials)
        print(json.dumps({"cell": ident, "completed_slots": len(history)}), flush=True)
    numeric = [{**t, "valid": t["valid"] is True} for t in history]
    summary = summarize(numeric, spec["budget"], spec["tolerance"])
    summary.update(cell=ident, filtered=sum(t["valid"] is None for t in history))
    ensure(directory / "complete.json", summary)
    return summary


def run(repo, root, allow_paid=False):
    m = verify_inputs(repo, root)
    spec = m["spec"]
    if not allow_paid and any(a in MODELS for a in spec["policies"]):
        raise ValueError("paid policies require explicit --allow-paid")
    with (root / "runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        meter = Meter(root, spec["cost_ceiling_usd"])
        cells = [
            (t, s, a) for t in spec["targets"] for s in spec["seeds"] for a in spec["policies"]
        ]
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=spec["max_workers"]) as pool:
                futures = [pool.submit(cell, root, m, *c, meter) for c in cells]
                try:
                    summaries = [f.result() for f in futures]
                except Exception:
                    meter.halted.set()
                    for f in futures:
                        f.cancel()
                    raise
            ensure(
                root / "complete.json",
                {
                    "cells": len(cells),
                    "slots": len(cells) * spec["budget"],
                    "summaries": summaries,
                    "liability_usd": meter.liability,
                },
            )
        except Exception as exc:
            write(
                root / f"failure-{time.time_ns()}.json",
                {"error": repr(exc), "pid": os.getpid()},
            )
            raise


def status(root):
    read(root / "manifest.json")
    cells = list(root.glob("panel/*/*/*/complete.json"))
    slots = sum(len(read(p)) for p in root.glob("panel/*/*/*/batches/*/trials.json"))
    return {
        "completed_cells": len(cells),
        "completed_slots": slots,
        "complete": (root / "complete.json").exists(),
        "failures": [str(p.name) for p in root.glob("failure-*.json")],
    }


def export(root, destination):
    """Retain compact records only; never move/delete scratch during export."""
    if not (root / "complete.json").exists():
        raise ValueError("only complete studies can be exported")
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            raise ValueError("export refuses symlinks")
        if not p.is_file() or p.suffix not in (".json", ".log", ".S"):
            continue
        if p.name.startswith("trace_"):
            continue
        rel = p.relative_to(root)
        if rel.parts[0] not in ("panel", "cache") and len(rel.parts) > 1:
            continue
        target = destination / (str(rel) + ".gz")
        target.parent.mkdir(parents=True, exist_ok=True)
        data = p.read_bytes()
        target.write_bytes(gzip.compress(data, mtime=0))
        hashes[str(rel)] = hashlib.sha256(data).hexdigest()
    write(destination / "inventory.json", hashes)
    return {"files": len(hashes), "destination": str(destination)}


def verify_export(directory):
    hashes = read(directory / "inventory.json")
    actual = {}
    for path in directory.rglob("*.gz"):
        if path.is_symlink():
            raise ValueError("export must not contain symlinks")
        relative = str(path.relative_to(directory))[:-3]
        actual[relative] = hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()
    if actual != hashes:
        raise ValueError("export inventory differs")
    return {"verified": True, "files": len(actual)}
