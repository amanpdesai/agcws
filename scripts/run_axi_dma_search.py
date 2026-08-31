#!/usr/bin/env python3
"""Run a proposal-counted DMA activity search through the coupled harness."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.axi_dma import AxiDmaAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies import RandomSearch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=float, default=0.5)
    parser.add_argument("--p-min", type=float, required=True)
    parser.add_argument("--p-max", type=float, required=True)
    parser.add_argument("--budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("out/axi-dma-search"))
    args = parser.parse_args()
    counter = 0

    def evaluate(workload: dict) -> PowerProfile:
        nonlocal counter
        counter += 1
        workload_path = args.out / "workloads" / f"workload-{counter:05d}.json"
        trial_dir = args.out / "evaluations" / f"trial-{counter:05d}"
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        subprocess.run(["bash", "scripts/run_axi_dma_coupled.sh", str(workload_path),
                        str(trial_dir)], check=True, capture_output=True, text=True)
        activity = json.loads((trial_dir / "activity.json").read_text())
        edges = max(1, int(activity["clock_edges"]))
        useful = sum(int(item["length"]) for item in workload["transfers"])
        return PowerProfile(
            mean_power=float(activity["total_transitions"]) / edges,
            peak_power=float(max(activity["per_cycle_toggles"] or [0])),
            windowed=tuple(activity["window_toggles"]),
            per_cycle_toggles=tuple(activity["per_cycle_toggles"]),
            useful_work=useful, valid=True, fidelity="activity",
            provenance={"oracle": "cocotb-axi-ram-vcd",
                         "metric": "total_transitions_per_clock_edge"},
        )

    trials = run_search(AxiDmaAdapter(), RandomSearch(args.seed),
                        ScalarGoal(args.target, 0.05), evaluate, budget=args.budget,
                        batch_size=4, seed=args.seed, p_min=args.p_min, p_max=args.p_max,
                        output_dir=args.out)
    print(json.dumps({"trials": len(trials), "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
