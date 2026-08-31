#!/usr/bin/env python3
"""Run the shared proposal-counted runner against an AES region target."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import CompositionalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch
from evaluate_aes_workload import evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-compositional-search"))
    parser.add_argument("--budget", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--power-floor", type=float, default=0.0)
    args = parser.parse_args()
    goal = CompositionalGoal(
        shares={"aes_core": 0.4, "aes_control": 0.2, "aes_data": 0.4},
        power_floor=args.power_floor,
    )
    adapter = AESAdapter()
    trial_index = 0

    def evaluator(workload: dict) -> PowerProfile:
        nonlocal trial_index
        trial_dir = args.out / "evaluations" / f"trial-{trial_index:05d}"
        workload_path = args.out / "workloads" / f"workload-{trial_index:05d}.json"
        trial_index += 1
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        result = evaluate(workload_path, args.synthesis_dir, trial_dir)
        activity = result["activity"]
        return PowerProfile(
            mean_power=result["mean_power"], peak_power=result["mean_power"],
            by_region=result["by_region"], per_cycle_toggles=activity["per_cycle_toggles"],
            windowed=activity["window_toggles"], useful_work=result["useful_work"],
            valid=True, fidelity="activity", provenance=result["provenance"],
        )

    trials = run_search(adapter, RandomSearch(args.seed), goal, evaluator,
                        budget=args.budget, batch_size=8, seed=args.seed,
                        output_dir=args.out)
    print(json.dumps({"trials": len(trials), "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
