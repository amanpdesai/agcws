#!/usr/bin/env python3
"""Run the proposal-counted baseline against an AES temporal target."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import TemporalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.temporal_search import TemporalRandomSearch
from agcws import config
from agcws.provenance import file_sha256, toolchain_record
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-temporal-search"))
    parser.add_argument("--budget", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    goal = TemporalGoal(windows=8, profile=[1.0, 0.7, 0.2, 0.2, 0.2, 0.7, 1.0, 0.7])
    adapter = AESAdapter()
    trial_index = 0

    def evaluator(workload: dict) -> PowerProfile:
        nonlocal trial_index
        trial_dir = args.out / "evaluations" / f"trial-{trial_index:05d}"
        trial_index += 1
        workload_path = _write_workload(args.out, trial_index, workload)
        # Temporal search uses the fast deterministic activity oracle. OpenSTA
        # is reserved for finalist validation; no temporal loss depends on its
        # scalar report.
        subprocess.run(
            [sys.executable, "scripts/run_aes_workload.py", str(workload_path),
             "--out", str(trial_dir)], check=True, capture_output=True, text=True,
        )
        log = (trial_dir / "run.log").read_text()
        match = re.search(r"AES_CORE_WORKLOAD_DONE blocks=(\d+)", log)
        if not match:
            raise RuntimeError("simulation log has no completed-work marker")
        activity = json.loads((trial_dir / "activity.json").read_text())
        return PowerProfile(mean_power=0.0, peak_power=0.0,
                            per_cycle_toggles=activity["per_cycle_toggles"],
                            windowed=activity["window_toggles"],
                            useful_work=float(match.group(1)), valid=True,
                            fidelity="activity", provenance={
                                "activity": "activity.json",
                                "workload_sha256": file_sha256(workload_path),
                                "activity_sha256": file_sha256(trial_dir / "activity.json"),
                                "oracle": "verilator-vcd",
                                "tools": toolchain_record({
                                    "verilator": (config.VERILATOR, ("--version",)),
                                }),
                            })

    trials = run_search(adapter, TemporalRandomSearch(args.seed), goal, evaluator,
                        budget=args.budget, batch_size=8, seed=args.seed,
                        output_dir=args.out)
    print(json.dumps({"trials": len(trials), "output": str(args.out.resolve())}, indent=2))


def _write_workload(root: Path, index: int, workload: dict) -> Path:
    path = root / "workloads" / f"workload-{index:05d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
    return path


if __name__ == "__main__":
    main()
