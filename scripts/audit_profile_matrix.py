#!/usr/bin/env python3
"""Audit that a profile aggregate matches its achieved-target manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path, nargs="+")
    parser.add_argument("aggregate", type=Path)
    parser.add_argument("--policies", nargs="+", required=True)
    parser.add_argument("--seeds", type=int, required=True)
    parser.add_argument("--budget", type=int, required=True)
    args = parser.parse_args()

    manifests = [json.loads(path.read_text()) for path in args.manifest]
    aggregate = json.loads(args.aggregate.read_text())
    available_sources = {
        f"{path}:{index}"
        for path, manifest in zip(args.manifest, manifests)
        for index in range(len(manifest.get("targets", [])))
    }
    actual_sources = {record.get("target_source") for record in aggregate}
    expected_groups = len(actual_sources) * len(args.policies)
    actual_policies = {record.get("policy") for record in aggregate}
    runs = {record.get("runs") for record in aggregate}
    slots = sum(record.get("runs", 0) * args.budget for record in aggregate)
    valid = sum(record.get("valid_trials", 0) for record in aggregate)
    errors = []
    if len(aggregate) != expected_groups:
        errors.append(f"groups={len(aggregate)} expected={expected_groups}")
    if actual_policies != set(args.policies):
        errors.append(f"policies={sorted(actual_policies)} expected={sorted(args.policies)}")
    if not actual_sources <= available_sources:
        errors.append(f"unknown_target_sources={sorted(actual_sources - available_sources)}")
    if runs != {args.seeds}:
        errors.append(f"runs={sorted(runs)} expected={args.seeds}")
    expected_slots = expected_groups * args.seeds * args.budget
    if slots != expected_slots:
        errors.append(f"slots={slots} expected={expected_slots}")
    result = {"aggregate": str(args.aggregate), "manifests": [str(path) for path in args.manifest],
              "groups": len(aggregate), "targets": len(actual_sources),
              "policies": sorted(actual_policies), "runs_per_group": sorted(runs),
              "proposal_slots": slots, "valid_trials": valid, "errors": errors,
              "valid": not errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
