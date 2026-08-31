#!/usr/bin/env python3
"""Measure the pre-registered AES random-search scalar solve fraction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch
from evaluate_aes_workload import evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-scalar-calibration"))
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--budget", type=int, default=20)
    parser.add_argument("--epsilon", type=float, default=0.05)
    args = parser.parse_args()
    if args.seeds <= 0 or args.budget <= 0:
        raise ValueError("seeds and budget must be positive")
    calibration = _find_calibration(args.synthesis_dir)
    p_min, p_max = calibration["p_min"], calibration["p_max"]
    adapter = AESAdapter()
    targets = [0.10, 0.25, 0.50, 0.75, 0.90]
    results = []
    for seed in range(args.seeds):
        for target in targets:
            run_dir = args.out / f"seed-{seed}" / f"target-{target:.2f}"
            run_dir.mkdir(parents=True, exist_ok=True)
            index = 0

            def evaluator(workload: dict) -> PowerProfile:
                nonlocal index
                index += 1
                workload_path = run_dir / f"workload-{index:04d}.json"
                workload_path.write_text(json.dumps(workload, sort_keys=True) + "\n")
                result = evaluate(workload_path, args.synthesis_dir, run_dir / f"eval-{index:04d}")
                return PowerProfile(mean_power=result["mean_power"], peak_power=result["mean_power"],
                                    useful_work=result["useful_work"], valid=True)

            trials = run_search(adapter, RandomSearch(seed), ScalarGoal(target, args.epsilon),
                                evaluator, budget=args.budget, batch_size=8, seed=seed,
                                p_min=p_min, p_max=p_max, output_dir=run_dir)
            scored = [trial for trial in trials if trial.profile is not None]
            solved = any(abs((trial.profile.mean_power - p_min) / (p_max - p_min) - target) <= args.epsilon
                         for trial in scored)
            results.append({"seed": seed, "target": target, "solved": solved,
                            "evaluations": len(trials), "valid_evaluations": len(scored)})
    solved_fraction = sum(item["solved"] for item in results) / len(results)
    report = {"targets": targets, "seeds": args.seeds, "budget": args.budget,
              "epsilon": args.epsilon, "p_min": p_min, "p_max": p_max,
              "solved_fraction": solved_fraction, "runs": results}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2))


def _find_calibration(synthesis_dir: Path) -> dict:
    candidate = synthesis_dir.parent / "aes-calibration-10" / "calibration.json"
    if not candidate.exists():
        raise FileNotFoundError(f"calibration.json not found: {candidate}")
    return json.loads(candidate.read_text())


if __name__ == "__main__":
    main()
