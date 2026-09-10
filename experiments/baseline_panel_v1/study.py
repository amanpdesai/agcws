"""Frozen construction, resumable parallel CPU panel, and compact archiving."""

import argparse
import concurrent.futures
import fcntl
import gzip
import os
import random
import subprocess
from pathlib import Path

import numpy as np

from agcws.provenance import file_sha256
from experiments.baseline_panel_v1.policies import ARMS, Control, witness_program
from experiments.gest_bridge_v1.bridge import upstream
from experiments.ibex_capability_v1.study import BINARY
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_depth_v1.study import evaluate
from experiments.ibex_temporal_v3.search import verify_runtime
from experiments.saga_temporal_v1.qualification import check_identity
from experiments.temporal_scaling_v1.smoke import EVIDENCE
from experiments.temporal_scaling_v1.targets import witnessed_target

FAMILIES = ("random", "phase-random", "scheduled-four-phase")


def freeze(root, archive, runtime):
    previous = Path("results/saga_temporal_v1")
    source = check_identity(previous)
    parent = read(previous / "parent_manifest.json")
    verify_runtime(parent, runtime)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    names = (
        set(source["sources"])
        | {str(p) for p in Path("experiments/baseline_panel_v1").glob("*.py")}
        | {"docs/BASELINE_PANEL_V1.md"}
    )
    sources = {}
    for name in sorted(names):
        if (
            subprocess.check_output(["git", "show", f"{commit}:{name}"])
            != Path(name).read_bytes()
        ):
            raise ValueError(f"uncommitted source {name}")
        sources[name] = file_sha256(Path(name))
    root.mkdir(parents=True, exist_ok=False)
    archive.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    os.link(runtime / BINARY, root / BINARY)
    write(archive / "parent_manifest.json", parent)
    write(
        archive / "manifest.json",
        {
            "phase": "CPU-only descriptive development panel",
            "source_commit": commit,
            "sources": sources,
            "upstream_sha256": source["upstream_sha256"],
            "parent_sha256": file_sha256(archive / "parent_manifest.json"),
            "numpy_version": np.__version__,
            "measurement_fingerprint": source["measurement_fingerprint"],
            "scale": source["scale"],
            "tolerance": source["tolerance"],
            "constructors": [
                {"name": family, "seed": 860 + i, "count": 4}
                for i, family in enumerate(FAMILIES)
            ],
            "selection": "first valid per constructor with normalized range >=0.05; all target vectors distinct",
            "minimum_range": 0.05,
            "seeds": [870, 871],
            "budget": 16,
            "arms": list(ARMS),
            "maximum_workers": 8,
        },
    )


def identity(archive):
    manifest = read(archive / "manifest.json")
    upstream()
    if np.__version__ != manifest["numpy_version"]:
        raise ValueError("numpy differs")
    if file_sha256(archive / "parent_manifest.json") != manifest["parent_sha256"]:
        raise ValueError("parent identity differs")
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"frozen source differs: {name}")
    return manifest


def committed(path):
    if subprocess.check_output(["git", "show", f"HEAD:{path}"]) != path.read_bytes():
        raise ValueError(f"commit input before execution: {path}")


def record(root, path, proposal, history, manifest):
    if path.exists():
        trial = read(path)
    elif not proposal["selected"]:
        trial = {
            **proposal,
            "status": "FILTERED",
            "valid": None,
            "rates": None,
            "loss": None,
        }
        write(path, trial)
    else:
        trial = evaluate(
            {
                "submitted": proposal["program"],
                "prediction": None,
                "prediction_error": None,
            },
            proposal["slot"],
            history,
            manifest,
            root,
            "baseline-panel-v1",
        )
        trial.update(proposal)
        trial["status"] = "MEASURED"
        write(path, trial)
    if any(trial[k] != v for k, v in proposal.items()):
        raise ValueError("resumed proposal differs")
    return trial


def choose(witnesses, manifest):
    targets = []
    for spec in manifest["constructors"]:
        candidates = [
            t
            for t in witnesses
            if t["constructor"] == spec["name"]
            and t["valid"]
            and (max(t["rates"]) - min(t["rates"])) / manifest["scale"]
            >= manifest["minimum_range"]
        ]
        if not candidates:
            raise ValueError(f"no qualifying witness for {spec['name']}")
        trial = candidates[0]
        targets.append(
            {
                "id": spec["name"],
                "witness_slot": trial["slot"],
                "target_rates": trial["rates"],
                "witness_cache_id": trial["cache_id"],
            }
        )
    if len({tuple(t["target_rates"]) for t in targets}) != len(targets):
        raise ValueError("selected target waveforms are not distinct")
    return targets


def archive_evaluations(root, archive, trials):
    for identifier in sorted({t["cache_id"] for t in trials if t.get("cache_id")}):
        for name in EVIDENCE:
            source = root / "cache" / identifier / name
            if not source.exists():
                continue
            destination = archive / "evaluations" / identifier / (name + ".gz")
            destination.parent.mkdir(parents=True, exist_ok=True)
            data = gzip.compress(source.read_bytes(), mtime=0)
            if destination.exists():
                if destination.read_bytes() != data:
                    raise ValueError("evidence changed")
            else:
                with destination.open("xb") as stream:
                    stream.write(data)


def construct(root, archive, manifest):
    def family(spec):
        rng, history = random.Random(spec["seed"]), []
        local = {**manifest, "target_rates": [0.0] * 8}
        for slot in range(1, spec["count"] + 1):
            proposal = {
                "slot": slot,
                "program": witness_program(spec["name"], rng, slot),
                "selected": True,
                "parents": [],
                "constructor": spec["name"],
            }
            ensure(
                root / "construction" / spec["name"] / f"{slot:03}.proposal.json",
                proposal,
            )
            trial = record(
                root,
                root / "construction" / spec["name"] / f"{slot:03}.json",
                proposal,
                [],
                local,
            )
            if trial["valid"]:
                witnessed_target(
                    trial["program"],
                    read(root / "cache" / trial["cache_id"] / "result.json"),
                    manifest["measurement_fingerprint"],
                    manifest["scale"],
                )
            history.append(trial)
            print(f"witness {spec['name']} {slot}: {trial['valid']}", flush=True)
        return history

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        groups = list(executor.map(family, manifest["constructors"]))
    witnesses = [t for group in groups for t in group]
    ensure(archive / "witnesses.json", witnesses)
    archive_evaluations(root, archive, witnesses)
    try:
        targets = choose(witnesses, manifest)
    except ValueError as exc:
        ensure(
            archive / "construction_failure.json",
            {"reason": str(exc), "attempts": len(witnesses)},
        )
        raise
    ensure(archive / "targets.json", targets)
    print(
        {"targets_ready": len(targets), "commit_targets_before_search": True},
        flush=True,
    )


def cell(root, archive, manifest, target, seed, arm):
    directory = root / "panel" / target["id"] / str(seed) / arm
    local = {**manifest, "target_rates": target["target_rates"]}
    control = Control(
        arm, seed, manifest["budget"], target["target_rates"], manifest["scale"]
    )
    history, decisions = [], []
    while control.used < control.budget:
        try:
            request = control.ask()
        except (ValueError, np.linalg.LinAlgError) as exc:
            delegate = control.delegate
            pending = [] if delegate is None else [p for _, p in delegate._pending]
            ensure(
                directory / "failure.json",
                {
                    "error": repr(exc),
                    "completed_slots": len(history),
                    "charged_slots": control.used
                    if delegate is None
                    else delegate.used,
                    "pending_proposals": pending,
                },
            )
            raise
        ensure(directory / "batches" / f"{control.used:03}.json", request)
        batch = [
            record(
                root, directory / "trials" / f"{p['slot']:03}.json", p, history, local
            )
            for p in request["proposals"]
        ]
        control.tell(batch)
        history.extend(batch)
        decisions.append(request)
    result = {
        "target": target["id"],
        "seed": seed,
        "arm": arm,
        "trials": history,
        "decisions": decisions,
    }
    ensure(directory / "complete.json", result)
    print({"cell_complete": [target["id"], seed, arm]}, flush=True)
    return result


def panel(root, archive, manifest):
    committed(archive / "targets.json")
    targets = read(archive / "targets.json")
    if targets != choose(read(archive / "witnesses.json"), manifest):
        raise ValueError("selected targets differ")
    cells = [
        (t, s, a) for t in targets for s in manifest["seeds"] for a in manifest["arms"]
    ]
    results, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=manifest["maximum_workers"]
    ) as executor:
        futures = {executor.submit(cell, root, archive, manifest, *c): c for c in cells}
        for future in concurrent.futures.as_completed(futures):
            t, s, a = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # noqa: BLE001 -- record worker failure, then fail the panel; never substitute results
                failures.append(
                    {"target": t["id"], "seed": s, "arm": a, "error": repr(exc)}
                )
    if failures:
        ensure(root / "panel_failure.json", failures)
        raise RuntimeError("incomplete panel; checkpoints retained, no replacements")
    results.sort(key=lambda c: (c["target"], c["seed"], c["arm"]))
    ensure(archive / "cells.json", results)
    archive_evaluations(root, archive, [t for c in results for t in c["trials"]])
    from experiments.baseline_panel_v1.audit import audit

    summary = audit(archive)
    ensure(archive / "summary.json", summary)
    ensure(
        root / "complete.json",
        {"cells": len(results), "proposals": sum(len(c["trials"]) for c in results)},
    )
    print(summary, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "construct", "panel", "audit"))
    parser.add_argument("--root", type=Path, default=Path("out/baseline-panel-v1"))
    parser.add_argument(
        "--archive", type=Path, default=Path("results/baseline_panel_v1")
    )
    parser.add_argument("--runtime", type=Path, default=Path("out/temporal-scaling-v1"))
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.archive, args.runtime)
    elif args.action == "audit":
        from experiments.baseline_panel_v1.audit import audit

        print(audit(args.archive))
    else:
        with (args.root / "run.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            manifest = identity(args.archive)
            committed(args.archive / "manifest.json")
            committed(args.archive / "parent_manifest.json")
            verify_runtime(read(args.archive / "parent_manifest.json"), args.root)
            (construct if args.action == "construct" else panel)(
                args.root, args.archive, manifest
            )


if __name__ == "__main__":
    main()
