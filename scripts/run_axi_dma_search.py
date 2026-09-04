#!/usr/bin/env python3
"""Run a proposal-counted DMA activity search through the coupled harness."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.axi_dma import AxiDmaAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies import (EvolutionarySearch, HybridSearch, MutationSearch,
                            OfflineAgent, OneShotAgent, RandomSearch, VertexAgent)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=float, default=0.5)
    parser.add_argument("--policy", choices=("random", "mutation", "evolutionary",
                                              "offline-agent", "one-shot-agent", "offline-hybrid", "vertex"),
                        default="random")
    parser.add_argument("--policies", help="comma-separated policy matrix; overrides --policy")
    parser.add_argument("--p-min", type=float, required=True)
    parser.add_argument("--p-max", type=float, required=True)
    parser.add_argument("--budget", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("out/axi-dma-search"))
    parser.add_argument("--model", default=os.environ.get("AGCWS_GEMINI_MODEL"))
    parser.add_argument("--project", default=os.environ.get("AGCWS_GCP_PROJECT"))
    parser.add_argument("--prompt", type=Path, default=ROOT / "prompts/agent_system_v1.txt")
    args = parser.parse_args()
    if args.policies:
        policies = [item.strip() for item in args.policies.split(",") if item.strip()]
        allowed = {"random", "mutation", "evolutionary", "offline-agent", "one-shot-agent", "offline-hybrid"}
        if not policies or any(item not in allowed for item in policies):
            parser.error("--policies contains an unknown policy")
        matrix = []
        for policy in policies:
            command = [sys.executable, str(Path(__file__).resolve()),
                       "--policy", policy, "--target", str(args.target),
                       "--p-min", str(args.p_min), "--p-max", str(args.p_max),
                       "--budget", str(args.budget), "--seed", str(args.seed),
                       "--out", str(args.out / policy)]
            completed = subprocess.run(command, check=True, text=True,
                                       capture_output=True)
            matrix.append(json.loads(completed.stdout))
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "matrix.json").write_text(
            json.dumps({"policies": matrix}, indent=2, sort_keys=True) + "\n"
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
            ["bash", "scripts/run_axi_dma_coupled.sh", str(workload_path),
             str(trial_dir)], check=False, capture_output=True, text=True,
            env={**__import__("os").environ, "AGCWS_PYTHON": sys.executable},
        )
        if completed.returncode:
            raise RuntimeError(
                "AXI-DMA coupled harness failed "
                f"(returncode={completed.returncode})\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
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

    policies = {"random": RandomSearch, "mutation": MutationSearch,
                "evolutionary": EvolutionarySearch, "offline-agent": OfflineAgent,
                "one-shot-agent": OneShotAgent}
    if args.policy == "vertex":
        if not args.model or not args.project:
            parser.error("vertex policy requires --model and --project")
        policy = VertexAgent.from_vertex(args.prompt.read_text(), model=args.model, project=args.project)
    elif args.policy == "offline-hybrid":
        agent = OfflineAgent(args.seed)
        policy = HybridSearch(agent.proposer, seed=args.seed,
                              model=agent.model, prompt_hash=agent.prompt_hash)
    else:
        policy = policies[args.policy](args.seed)
    policy.name = args.policy
    trials = run_search(AxiDmaAdapter(), policy,
                        ScalarGoal(args.target, 0.05), evaluate, budget=args.budget,
                        batch_size=4, seed=args.seed, p_min=args.p_min, p_max=args.p_max,
                        output_dir=args.out)
    print(json.dumps({"trials": len(trials), "policy": args.policy,
                      "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
