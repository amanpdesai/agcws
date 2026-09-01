#!/usr/bin/env python3
"""Build a reproducible Ibex RTL-activity envelope for target normalization."""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.ibex import IbexAdapter
from agcws.provenance import toolchain_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("out/ibex-activity-calibration"))
    args = parser.parse_args()
    if args.samples <= 0:
        parser.error("--samples must be positive")
    args.out.mkdir(parents=True, exist_ok=True)
    adapter = IbexAdapter()
    rng = random.Random(args.seed)
    records = []
    for index in range(args.samples):
        workload = adapter.random_workload(rng)
        workload_path = args.out / "workloads" / f"workload-{index:05d}.json"
        artifact = args.out / "evaluations" / f"trial-{index:05d}"
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        completed = subprocess.run(
            ["bash", "scripts/run_ibex_workload.sh", str(workload_path), str(artifact)],
            check=False, capture_output=True, text=True,
            env={**os.environ, "AGCWS_PYTHON": sys.executable},
        )
        if completed.returncode:
            raise RuntimeError(f"Ibex calibration trial {index} failed:\n{completed.stderr}")
        activity = json.loads((artifact / "activity.json").read_text())
        result = json.loads((artifact / "result.json").read_text())
        if not result["valid"]:
            raise RuntimeError(f"Ibex calibration trial {index} failed useful-work gate")
        edges = max(1, int(activity["clock_edges"]))
        records.append({
            "trial": index,
            "workload": workload,
            "activity": float(activity["total_transitions"]) / edges,
            "clock_edges": edges,
            "useful_work": result["useful_work"],
            "activity_path": str((artifact / "activity.json").resolve()),
            "result_path": str((artifact / "result.json").resolve()),
        })
    values = [record["activity"] for record in records]
    output = {"design": "ibex", "seed": args.seed, "samples": records,
              "p_min": min(values), "p_max": max(values),
              "metric": "total_transitions_per_clock_edge", "fidelity": "activity",
              "tools": toolchain_record({
                  "verilator": (os.environ.get("AGCWS_VERILATOR", "verilator"), ("--version",)),
                  "riscv_gcc": (os.environ.get("AGCWS_RISCV_GCC", "riscv64-unknown-elf-gcc"), ("--version",)),
                  "fst2vcd": (os.environ.get("AGCWS_FST2VCD", "fst2vcd"), ("--version",)),
              })}
    (args.out / "calibration.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"samples": len(records), "p_min": min(values), "p_max": max(values),
                      "output": str((args.out / "calibration.json").resolve())}, indent=2))


if __name__ == "__main__":
    main()
