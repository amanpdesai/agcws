#!/usr/bin/env python3
"""Run the shared proposal-counted runner against an AES region target."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import CompositionalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch
from agcws import config
from agcws.nodes.activity import attribute_regions
from agcws.provenance import file_sha256, toolchain_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-compositional-search"))
    parser.add_argument("--budget", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--power-floor", type=float, default=0.0)
    parser.add_argument("--targets", type=Path,
                        help="achieved-profile target manifest from select_profile_targets.py")
    parser.add_argument("--target-index", type=int, default=0)
    args = parser.parse_args()
    target_source = "built-in-smoke-target"
    shares = {"aes_core": 0.4, "aes_control": 0.2, "aes_data": 0.4}
    if args.targets:
        manifest = json.loads(args.targets.read_text())
        targets = manifest.get("targets", [])
        if not targets or not 0 <= args.target_index < len(targets):
            raise ValueError("target-index is outside the target manifest")
        shares = targets[args.target_index]["shares"]
        target_source = f"{args.targets}:{args.target_index}"
    goal = CompositionalGoal(shares=shares, power_floor=args.power_floor)
    adapter = AESAdapter()
    trial_index = 0

    def evaluator(workload: dict) -> PowerProfile:
        nonlocal trial_index
        trial_dir = args.out / "evaluations" / f"trial-{trial_index:05d}"
        workload_path = args.out / "workloads" / f"workload-{trial_index:05d}.json"
        trial_index += 1
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        completed = subprocess.run(
            [sys.executable, "scripts/run_aes_workload.py", str(workload_path),
             "--out", str(trial_dir)], check=False, capture_output=True, text=True,
        )
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(
                f"activity simulation failed with exit code {completed.returncode}: {detail}"
            )
        log = (trial_dir / "run.log").read_text()
        match = re.search(r"AES_CORE_WORKLOAD_DONE blocks=(\d+)", log)
        if not match:
            raise RuntimeError("simulation log has no completed-work marker")
        activity = json.loads((trial_dir / "activity.json").read_text())
        edges = max(1, int(activity["clock_edges"]))
        return PowerProfile(
            mean_power=float(activity["total_transitions"]) / edges,
            peak_power=float(max(activity["per_cycle_toggles"] or [0])),
            by_region=attribute_regions(activity["signal_transitions"],
                                         adapter.activity_region_prefixes),
            per_cycle_toggles=activity["per_cycle_toggles"],
            windowed=activity["window_toggles"],
            useful_work=float(match.group(1)), valid=True, fidelity="activity",
            provenance={"oracle": "verilator-vcd",
                        "metric": "total_transitions_per_clock_edge",
                        "workload_sha256": file_sha256(workload_path),
                        "activity_sha256": file_sha256(trial_dir / "activity.json"),
                        "tools": toolchain_record({
                            "verilator": (config.VERILATOR, ("--version",)),
                        })},
        )

    trials = run_search(adapter, RandomSearch(args.seed), goal, evaluator,
                        budget=args.budget, batch_size=8, seed=args.seed,
                        output_dir=args.out)
    (args.out / "target.json").write_text(json.dumps({"source": target_source,
        "goal": {"shares": goal.shares, "power_floor": goal.power_floor}}, indent=2) + "\n")
    print(json.dumps({"trials": len(trials), "output": str(args.out.resolve()),
                      "target_source": target_source}, indent=2))


if __name__ == "__main__":
    main()
