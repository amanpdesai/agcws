"""Archive and describe every declared CPU pilot cell, without significance claims."""

import argparse
import collections
import itertools
import json
import math
import shutil
import statistics
from pathlib import Path

from agcws.provenance import file_sha256


def describe(manifest, cells):
    expected = set(
        itertools.product(manifest["targets"], manifest["seeds"], manifest["policies"])
    )
    actual = {(s["target"], s["seed"], s["policy"]) for s, _ in cells}
    if actual != expected or len(cells) != len(expected):
        raise ValueError(f"incomplete/duplicate panel: missing {expected - actual}")
    scale = manifest["scale"]
    output = {}
    for policy in manifest["policies"]:
        selected = [(s, t) for s, t in cells if s["policy"] == policy]
        trials = [t for _, rows in selected for t in rows]
        if any(
            len(rows) != manifest["budget"]
            or [t["slot"] for t in rows] != list(range(1, manifest["budget"] + 1))
            for _, rows in selected
        ):
            raise ValueError("incomplete proposal accounting")
        states = collections.Counter(
            "VALID" if t["valid"] else t["stage"] for t in trials
        )
        # Fixed grid, development descriptive only; not intrinsic language expressiveness.
        profiles = {
            tuple(math.floor(v / (0.1 * scale)) for v in t["rates"])
            for t in trials
            if t["valid"]
        }
        output[policy] = {
            "cells": len(selected),
            "mean_auc": statistics.mean(s["auc"] for s, _ in selected),
            "mean_final_loss": statistics.mean(s["final_loss"] for s, _ in selected),
            "solved_cells": sum(s["solved"] for s, _ in selected),
            "mean_censored_proposals": statistics.mean(
                s["evaluations_to_target"] for s, _ in selected
            ),
            "targets_solved_any_seed": sorted(
                {s["target"] for s, _ in selected if s["solved"]}
            ),
            "validity": dict(states),
            "grid_profiles": len(profiles),
            "grid_width_transitions_per_edge": 0.1 * scale,
            "est_cost_usd": sum(s["est_cost_usd"] for s, _ in selected),
            "unknown_usage_batches": sum(
                s["unknown_usage_batches"] for s, _ in selected
            ),
            "per_target": {
                target: {
                    "mean_auc": statistics.mean(
                        s["auc"] for s, _ in selected if s["target"] == target
                    ),
                    "solved": sum(
                        s["solved"] for s, _ in selected if s["target"] == target
                    ),
                }
                for target in manifest["targets"]
            },
        }
    return {
        "phase": "development-only",
        "policies": output,
        "limitations": [
            "three development seeds, four achieved target profiles; no inferential claim",
            "same language; finite-budget coverage is not intrinsic expressiveness",
            "grid diversity is an exploratory descriptor, not the primary endpoint",
            "RTL core activity, not gate power; no causal isolation of semantics",
        ],
    }


def archive(root, destination):
    manifest_path = destination / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    cells = []
    for target, seed, policy in itertools.product(
        manifest["targets"], manifest["seeds"], manifest["policies"]
    ):
        relative = Path("panel") / target / f"seed-{seed}" / policy
        source = root / relative
        summary = json.loads((source / "summary.json").read_text())
        rows = [
            json.loads(line)
            for line in (source / "trials.jsonl").read_text().splitlines()
        ]
        cells.append((summary, rows))
        (destination / relative).mkdir(parents=True, exist_ok=True)
        for name in ("summary.json", "trials.jsonl", "batches.json", "manifest.json"):
            shutil.copy2(source / name, destination / relative / name)
    report = describe(manifest, cells)
    (destination / "aggregate.json").write_text(json.dumps(report, indent=2) + "\n")
    for name in manifest["sources"]:
        path = Path(name)
        if file_sha256(path) != manifest["sources"][name]:
            raise ValueError(f"frozen source changed: {name}")
        target = destination / "sources" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copy2(root / "gate.json", destination / "gate.json")
    shutil.copytree(root / "gate-inputs", destination / "witnesses", dirs_exist_ok=True)
    identifiers = {t["cache_id"] for _, rows in cells for t in rows if t["cache_id"]}
    for identifier in sorted(identifiers):
        target = destination / "evaluations" / identifier
        target.mkdir(parents=True, exist_ok=True)
        source = root / "cache" / identifier
        for name in (
            "program.json",
            "result.json",
            "run/functional.json",
            "run/profile.json",
        ):
            path = source / name
            if path.exists():
                (target / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target / name)
    index = {
        str(p.relative_to(destination)): file_sha256(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file() and p.name != "sha256.json"
    }
    (destination / "sha256.json").write_text(json.dumps(index, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    archive(args.root, args.archive)
