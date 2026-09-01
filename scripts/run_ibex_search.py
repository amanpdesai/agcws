#!/usr/bin/env python3
"""Run a proposal-counted Ibex activity search through the simple system."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.ibex import IbexAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies import (EvolutionarySearch, HybridSearch, MutationSearch,
                            OfflineAgent, OneShotAgent, RandomSearch)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=float, default=0.5)
    choices = ("random", "mutation", "evolutionary", "offline-agent",
               "one-shot-agent", "offline-hybrid")
    parser.add_argument("--policy", choices=choices, default="random")
    parser.add_argument("--policies", help="comma-separated policy matrix; overrides --policy")
    parser.add_argument("--p-min", type=float)
    parser.add_argument("--p-max", type=float)
    parser.add_argument("--calibration", type=Path,
                        help="calibration.json containing p_min and p_max")
    parser.add_argument("--budget", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seeds", help="comma-separated seed matrix; overrides --seed")
    parser.add_argument("--out", type=Path, default=Path("out/ibex-search"))
    args = parser.parse_args()
    if args.calibration:
        calibration = json.loads(args.calibration.read_text())
        try:
            args.p_min = float(calibration["p_min"])
            args.p_max = float(calibration["p_max"])
        except (KeyError, TypeError, ValueError) as exc:
            parser.error(f"invalid Ibex calibration: {exc}")
    if args.p_min is None or args.p_max is None or args.p_max <= args.p_min:
        parser.error("provide --calibration or valid --p-min/--p-max bounds")
    if args.seeds:
        try:
            seeds = [int(item.strip()) for item in args.seeds.split(",") if item.strip()]
        except ValueError as exc:
            parser.error(f"invalid seed matrix: {exc}")
        if not seeds:
            parser.error("--seeds must contain at least one integer")
        results = []
        for seed in seeds:
            command = [sys.executable, str(Path(__file__).resolve()),
                       "--policy", args.policy, "--target", str(args.target),
                       "--p-min", str(args.p_min), "--p-max", str(args.p_max),
                       "--budget", str(args.budget), "--seed", str(seed),
                       "--out", str(args.out / f"seed-{seed}")]
            if args.policies:
                command.extend(["--policies", args.policies])
            if args.calibration:
                command.extend(["--calibration", str(args.calibration)])
            completed = subprocess.run(command, check=True, text=True, capture_output=True)
            results.append(json.loads(completed.stdout))
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "seeds.json").write_text(
            json.dumps({"seeds": results}, indent=2, sort_keys=True) + "\n"
        )
        print(json.dumps({"seeds": seeds, "output": str(args.out.resolve())}, indent=2))
        return
    if args.policies:
        policies = [item.strip() for item in args.policies.split(",") if item.strip()]
        allowed = set(choices)
        if not policies or any(item not in allowed for item in policies):
            parser.error("--policies contains an unknown policy")
        results = []
        for policy in policies:
            command = [sys.executable, str(Path(__file__).resolve()),
                       "--policy", policy, "--target", str(args.target),
                       "--p-min", str(args.p_min), "--p-max", str(args.p_max),
                       "--budget", str(args.budget), "--seed", str(args.seed),
                       "--out", str(args.out / policy)]
            completed = subprocess.run(command, check=True, text=True, capture_output=True)
            results.append(json.loads(completed.stdout))
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "matrix.json").write_text(
            json.dumps({"policies": results}, indent=2, sort_keys=True) + "\n"
        )
        print(json.dumps({"policies": policies, "output": str(args.out.resolve())}, indent=2))
        return
    counter = 0

    def evaluate(workload: dict) -> PowerProfile:
        nonlocal counter
        counter += 1
        workload_path = args.out / "workloads" / f"workload-{counter:05d}.json"
        trial_dir = args.out / "evaluations" / f"trial-{counter:05d}"
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        completed = subprocess.run(
            ["bash", "scripts/run_ibex_workload.sh", str(workload_path), str(trial_dir)],
            check=False, capture_output=True, text=True,
            env={**os.environ, "AGCWS_PYTHON": sys.executable},
        )
        if completed.returncode:
            raise RuntimeError(f"Ibex harness failed (returncode={completed.returncode})\n{completed.stderr}")
        activity = json.loads((trial_dir / "activity.json").read_text())
        edges = max(1, int(activity["clock_edges"]))
        return PowerProfile(
            mean_power=float(activity["total_transitions"]) / edges,
            peak_power=float(max(activity["per_cycle_toggles"] or [0])),
            windowed=tuple(activity["window_toggles"]),
            per_cycle_toggles=tuple(activity["per_cycle_toggles"]),
            useful_work=float(json.loads((trial_dir / "result.json").read_text())["useful_work"]),
            valid=True, fidelity="activity",
            provenance={"oracle": "ibex-simple-system-vcd", "metric": "total_transitions_per_clock_edge"},
        )

    policies = {"random": RandomSearch, "mutation": MutationSearch,
                "evolutionary": EvolutionarySearch,
                "offline-agent": OfflineAgent, "one-shot-agent": OneShotAgent}
    if args.policy == "offline-hybrid":
        agent = OfflineAgent(args.seed)
        policy = HybridSearch(agent.proposer, seed=args.seed,
                              model=agent.model, prompt_hash=agent.prompt_hash)
    else:
        policy = policies[args.policy](args.seed)
    trials = run_search(IbexAdapter(), policy, ScalarGoal(args.target, 0.05), evaluate,
                        budget=args.budget, batch_size=1, seed=args.seed,
                        p_min=args.p_min, p_max=args.p_max, output_dir=args.out)
    print(json.dumps({"trials": len(trials), "policy": args.policy,
                      "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
