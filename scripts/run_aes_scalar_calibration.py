#!/usr/bin/env python3
"""Measure the pre-registered AES random-search scalar solve fraction."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch
from agcws.nodes.validation import validate_static
from agcws.adapters.base import SimResult


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-scalar-calibration"))
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--budget", type=int, default=20)
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--calibration", type=Path,
                        help="calibration.json produced from the selected corpus")
    args = parser.parse_args()
    if args.seeds <= 0 or args.budget <= 0:
        raise ValueError("seeds and budget must be positive")
    calibration = (json.loads(args.calibration.read_text())
                   if args.calibration else _find_calibration(args.synthesis_dir))
    p_min, p_max = calibration["p_min"], calibration["p_max"]
    adapter = AESAdapter()
    targets = [0.10, 0.25, 0.50, 0.75, 0.90]
    results = []
    for seed in range(args.seed_start, args.seed_start + args.seeds):
        for target in targets:
            run_dir = args.out / f"seed-{seed}" / f"target-{target:.2f}"
            run_dir.mkdir(parents=True, exist_ok=True)
            cell_summary = run_dir / "summary.json"
            if cell_summary.exists():
                results.append(json.loads(cell_summary.read_text()))
                continue
            index = 0

            def evaluator(workload: dict) -> PowerProfile:
                nonlocal index
                index += 1
                workload_path = run_dir / f"workload-{index:04d}.json"
                workload_path.write_text(json.dumps(workload, sort_keys=True) + "\n")
                eval_dir = run_dir / f"eval-{index:04d}"
                validity = validate_static(adapter, workload)
                if not validity.valid:
                    return PowerProfile(mean_power=0.0, peak_power=0.0,
                                        useful_work=0.0, valid=False,
                                        fidelity="activity", provenance={"invalid_stage": validity.stage.value,
                                                                          "invalid_reason": validity.reason})
                eval_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run([sys.executable, "scripts/run_aes_workload.py",
                                str(workload_path), "--out", str(eval_dir)], check=True)
                log = (eval_dir / "run.log").read_text()
                match = re.search(r"AES_CORE_WORKLOAD_DONE blocks=(\d+)", log)
                if not match:
                    raise RuntimeError("simulation log has no completed-work marker")
                blocks = int(match.group(1))
                runtime_validity = adapter.validate_result(
                    SimResult(True, True, True, blocks))
                if not runtime_validity.valid:
                    return PowerProfile(mean_power=0.0, peak_power=0.0,
                                        useful_work=blocks, valid=False,
                                        fidelity="activity", provenance={"invalid_stage": runtime_validity.stage.value,
                                                                          "invalid_reason": runtime_validity.reason})
                activity = json.loads((eval_dir / "activity.json").read_text())
                cycles = max(1, int(activity["clock_edges"]))
                proxy = float(activity["total_transitions"]) / cycles
                return PowerProfile(mean_power=proxy, peak_power=max(activity["per_cycle_toggles"]),
                                    useful_work=blocks, valid=True, fidelity="activity",
                                    provenance={"metric": "total_transitions_per_clock_edge",
                                                "activity": "activity.json"})

            trials = run_search(adapter, RandomSearch(seed), ScalarGoal(target, args.epsilon),
                                evaluator, budget=args.budget, batch_size=8, seed=seed,
                                p_min=p_min, p_max=p_max, output_dir=run_dir)
            scored = [trial for trial in trials if trial.profile is not None]
            solved = any(abs((trial.profile.mean_power - p_min) / (p_max - p_min) - target) <= args.epsilon
                         for trial in scored)
            cell = {"seed": seed, "target": target, "solved": solved,
                    "evaluations": len(trials), "valid_evaluations": len(scored)}
            cell_summary.write_text(json.dumps(cell, indent=2, sort_keys=True) + "\n")
            results.append(cell)
    solved_fraction = sum(item["solved"] for item in results) / len(results)
    report = {"targets": targets, "seed_start": args.seed_start, "seeds": args.seeds, "budget": args.budget,
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
