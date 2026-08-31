#!/usr/bin/env python3
"""Build a reproducible AES random calibration corpus."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.nodes.validation import validate_static
from agcws.policies.random_search import RandomSearch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("out/aes-calibration"))
    args = parser.parse_args()
    if args.count <= 0:
        raise ValueError("count must be positive")
    args.out.mkdir(parents=True, exist_ok=True)
    policy = RandomSearch(args.seed)
    adapter = AESAdapter()
    records = []
    for index, workload in enumerate(policy.propose(adapter, None, [], args.count)):
        validity = validate_static(adapter, workload)
        if not validity.valid:
            raise ValueError(f"random policy emitted invalid workload: {validity.reason}")
        workload_path = args.out / f"workload-{index:04d}.json"
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        trial_dir = args.out / f"trial-{index:04d}"
        subprocess.run([
            sys.executable, "scripts/evaluate_aes_workload.py", str(workload_path),
            str(args.synthesis_dir), "--out", str(trial_dir), "--allow-invalid",
        ], check=True)
        result = json.loads((trial_dir / "result.json").read_text())
        records.append({"index": index, "seed": args.seed, "workload": workload, **result})
    valid_records = [record for record in records if record.get("valid")]
    if not valid_records:
        raise RuntimeError("random corpus contains no valid non-idle workloads")
    powers = [float(record["mean_power"]) for record in valid_records]
    (args.out / "corpus.jsonl").write_text("\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n")
    (args.out / "summary.json").write_text(json.dumps({
        "count": len(records), "valid_count": len(valid_records),
        "invalid_count": len(records) - len(valid_records), "seed": args.seed,
        "p_min": min(powers), "p_max": max(powers),
        "mean": sum(powers) / len(powers),
    }, indent=2) + "\n")
    print(json.dumps(json.loads((args.out / "summary.json").read_text()), indent=2))


if __name__ == "__main__":
    main()
