"""Frozen CPU-only qualification; no model calls or efficacy inference."""

import argparse
import gzip
import json
import os
import random
import subprocess
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_capability_v1.study import BINARY
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_depth_v1.study import evaluate
from experiments.ibex_temporal_v3.program import random_program
from experiments.ibex_temporal_v3.search import verify_runtime
from experiments.temporal_scaling_v1.baselines import phase_ga, phase_random
from experiments.temporal_scaling_v1.targets import (
    FAMILIES,
    Request,
    generate,
    witnessed_target,
)

ARMS = ("legacy-random", "phase-random", "phase-ga")
EVIDENCE = (
    "result.json",
    "program.json",
    "driver.log",
    "run/program.S",
    "run/functional.json",
    "run/profile.json",
    "run/feedback.json",
    "run/execution.json",
    "run/phase_map.json",
    "run/ibex_simple_system.log",
    "run/compile.log",
    "run/simulator.log",
)


def propose(arm, rng, slot, history):
    if arm not in ARMS:
        raise ValueError("unknown policy")
    if slot <= 2 or arm == "legacy-random":
        return random_program(rng), {
            "operator": "shared-initial" if slot <= 2 else "legacy-random",
            "parents": [],
        }
    if arm == "phase-random":
        return phase_random(rng, slot), {"operator": "phase-random", "parents": []}
    if arm == "phase-ga":
        return phase_ga(rng, slot, history)
    raise ValueError("unknown policy")


def freeze(root, archive, runtime):
    parent_path = Path("results/ibex_temporal_v4_development/manifest.json")
    parent = read(parent_path)
    verify_runtime(parent, runtime)
    root.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    os.link(runtime / BINARY, root / BINARY)
    archive.mkdir(parents=True, exist_ok=False)
    write(archive / "parent_manifest.json", parent)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    names = (
        set(parent["sources"])
        | {
            str(p)
            for folder in (
                "experiments/ibex_depth_v1",
                "experiments/temporal_scaling_v1",
            )
            for p in Path(folder).glob("*.py")
        }
        | {
            "experiments/ibex_capability_v1/study.py",
            "docs/TEMPORAL_SCALING_V1_PLAN.md",
        }
    )
    sources = {}
    for name in sorted(names):
        data = subprocess.check_output(["git", "show", f"{commit}:{name}"])
        if data != Path(name).read_bytes():
            raise ValueError(f"uncommitted source: {name}")
        target = archive / "sources" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        sources[name] = file_sha256(target)
    write(
        archive / "manifest.json",
        {
            "phase": "CPU-only-qualification-not-comparative-inference",
            "source_commit": commit,
            "sources": sources,
            "parent_sha256": file_sha256(parent_path),
            "measurement_fingerprint": parent["measurement_fingerprint"],
            "scale": parent["scale"],
            "tolerance": parent["tolerance"],
            "witness_seed": 820,
            "witness_proposals": 12,
            "target_count": 2,
            "minimum_normalized_range": 0.05,
            "search_seed": 830,
            "arms": list(ARMS),
            "budget": 12,
            "batch_size": 2,
            "requests": [
                generate(Request(seed=901, family=family, horizon_cycles=h, bins=b))
                for h, b in (
                    (200000, 8),
                    (400000, 8),
                    (800000, 8),
                    (200000, 16),
                    (200000, 32),
                )
                for family in FAMILIES
            ],
            "selection": "first two valid witnesses with normalized range >= 0.05; no replacement draws",
        },
    )


def record_candidate(path, program, slot, history, manifest, root, operator):
    if path.exists():
        trial = read(path)
        if trial["program"] != program or trial["operator"] != operator:
            raise ValueError("resume proposal differs")
        return trial
    trial = evaluate(
        {"submitted": program, "prediction": None, "prediction_error": None},
        slot,
        history,
        manifest,
        root,
        "cpu-qualification",
    )
    trial["operator"] = operator
    write(path, trial)
    print(
        json.dumps(
            {"path": str(path), "valid": trial["valid"], "stage": trial["stage"]}
        ),
        flush=True,
    )
    return trial


def run(root, archive):
    import fcntl

    with (root / "qualification.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = read(archive / "manifest.json")
        for name, sha in manifest["sources"].items():
            if file_sha256(Path(name)) != sha:
                raise ValueError(f"frozen source changed: {name}")
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{archive}/manifest.json"]
        )
        if committed != (archive / "manifest.json").read_bytes():
            raise ValueError("commit manifest before execution")
        verify_runtime(read(archive / "parent_manifest.json"), root)
        witnesses, targets = [], []
        rng = random.Random(manifest["witness_seed"])
        neutral = {**manifest, "target_rates": [0.0] * 8}
        for slot in range(1, manifest["witness_proposals"] + 1):
            trial = record_candidate(
                root / "witnesses" / f"{slot:03}.json",
                phase_random(rng, slot),
                slot,
                witnesses,
                neutral,
                root,
                {"operator": "witness-phase-random", "parents": []},
            )
            witnesses.append(trial)
            if trial["valid"]:
                result = read(root / "cache" / trial["cache_id"] / "result.json")
                target = witnessed_target(
                    trial["program"],
                    result,
                    manifest["measurement_fingerprint"],
                    manifest["scale"],
                )
                if (
                    max(target["target_rates"]) - min(target["target_rates"])
                ) / manifest["scale"] >= manifest["minimum_normalized_range"]:
                    targets.append(target)
        selected = targets[: manifest["target_count"]]
        ensure(root / "targets.json", selected)
        if len(selected) != manifest["target_count"]:
            write(
                root / "qualification_failure.json",
                {
                    "reason": "insufficient nonflat valid witnesses",
                    "found": len(selected),
                },
            )
            raise RuntimeError("witness qualification failed; do not resample")
        for index, target in enumerate(selected):
            for arm in manifest["arms"]:
                history, rng = [], random.Random(manifest["search_seed"])
                cell = root / "panel" / str(index) / arm
                for start in range(1, manifest["budget"] + 1, 2):
                    batch = [
                        (slot, *propose(arm, rng, slot, history))
                        for slot in (start, start + 1)
                    ]
                    trials = [
                        record_candidate(
                            cell / f"{slot:03}.json",
                            program,
                            slot,
                            history,
                            {**manifest, "target_rates": target["target_rates"]},
                            root,
                            operator,
                        )
                        for slot, program, operator in batch
                    ]
                    history.extend(trials)
                ensure(
                    cell / "summary.json",
                    summarize(history, manifest["budget"], manifest["tolerance"]),
                )
        ensure(
            root / "complete.json",
            {"witness_proposals": 12, "search_slots": 72, "cells": 6},
        )


def archive_evidence(root, destination):
    from analysis.temporal_scaling_v1 import audit, verify

    read(root / "complete.json")
    identifiers = set()
    for folder in ("witnesses", "panel"):
        for path in sorted((root / folder).rglob("*.json")):
            target = destination / path.relative_to(root)
            ensure(target, read(path))
            if path.name != "summary.json":
                identifiers.add(read(path)["cache_id"])
    for name in ("targets.json", "complete.json"):
        ensure(destination / name, read(root / name))
    for identifier in sorted(identifiers):
        for name in EVIDENCE:
            source = root / "cache" / identifier / name
            if source.exists():
                target = destination / "evaluations" / identifier / (name + ".gz")
                target.parent.mkdir(parents=True, exist_ok=True)
                data = gzip.compress(source.read_bytes(), mtime=0)
                if target.exists() and target.read_bytes() != data:
                    raise ValueError("immutable compressed evidence differs")
                target.write_bytes(data)
    summary = audit(destination)
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    (destination / "sha256.json").write_text(
        json.dumps(
            {
                str(p.relative_to(destination)): file_sha256(p)
                for p in sorted(destination.rglob("*"))
                if p.is_file() and p.name != "sha256.json"
            },
            indent=2,
        )
        + "\n"
    )
    return verify(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run", "archive"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, default=Path("out/ibex-depth-v1"))
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.archive, args.runtime)
    elif args.action == "run":
        run(args.root, args.archive)
    else:
        print(json.dumps(archive_evidence(args.root, args.archive), indent=2))
