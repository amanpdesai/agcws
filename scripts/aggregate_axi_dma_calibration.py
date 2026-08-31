#!/usr/bin/env python3
"""Aggregate coupled AXI-DMA random-search outputs into calibration metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records = []
    for root in args.roots:
        trials_path = root / "trials.jsonl"
        if not trials_path.is_file():
            raise FileNotFoundError(trials_path)
        for line in trials_path.read_text().splitlines():
            trial = json.loads(line)
            if trial["validity"]["valid"] and trial.get("profile"):
                records.append({
                    "source": str(root),
                    "workload_sha256": sha256(root / "workloads" /
                                               f"workload-{int(trial['trial_id'].rsplit('-', 1)[-1]) + 1:05d}.json"),
                    "mean_power": float(trial["profile"]["mean_power"]),
                    "fidelity": trial["profile"]["fidelity"],
                })
    if not records:
        raise RuntimeError("no valid calibration records found")
    powers = [record["mean_power"] for record in records]
    result = {
        "design": "verilog_axi_dma",
        "oracle": "cocotb-axi-ram-vcd",
        "metric": "total_transitions_per_clock_edge",
        "source_roots": [str(root) for root in args.roots],
        "valid_count": len(records),
        "p_min": min(powers),
        "p_max": max(powers),
        "distinct_values": len(set(powers)),
        "records": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in
                      ("valid_count", "p_min", "p_max", "distinct_values")}, indent=2))


if __name__ == "__main__":
    main()
