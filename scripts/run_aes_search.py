#!/usr/bin/env python3
"""Run one declared AES scalar policy through the common search runner."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies import EvolutionarySearch, MutationSearch, OfflineAgent, RandomSearch
from evaluate_aes_workload import evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--policy", choices=("random", "mutation", "evolutionary", "offline-agent"), default="random")
    parser.add_argument("--target", type=float, default=0.5)
    parser.add_argument("--epsilon", type=float, default=0.10)
    parser.add_argument("--p-min", type=float, required=True)
    parser.add_argument("--p-max", type=float, required=True)
    parser.add_argument("--budget", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("out/aes-search"))
    args = parser.parse_args()
    policies = {"random": RandomSearch, "mutation": MutationSearch,
                "evolutionary": EvolutionarySearch, "offline-agent": OfflineAgent}
    policy = policies[args.policy](args.seed)
    counter = 0

    def evaluator(workload: dict) -> PowerProfile:
        nonlocal counter
        counter += 1
        workload_path = args.out / "workloads" / f"workload-{counter:05d}.json"
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        result = evaluate(workload_path, args.synthesis_dir, args.out / "evaluations" / f"trial-{counter:05d}")
        return PowerProfile(mean_power=result["mean_power"], peak_power=result["mean_power"],
                            useful_work=result["useful_work"], valid=True,
                            fidelity="synthesis", provenance=result["provenance"])

    trials = run_search(AESAdapter(), policy, ScalarGoal(args.target, args.epsilon), evaluator,
                        budget=args.budget, batch_size=8, seed=args.seed,
                        p_min=args.p_min, p_max=args.p_max, output_dir=args.out)
    print(json.dumps({"policy": args.policy, "trials": len(trials), "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
