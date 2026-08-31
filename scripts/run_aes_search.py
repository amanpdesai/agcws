#!/usr/bin/env python3
"""Run one declared AES scalar policy through the common search runner."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws import config
from agcws.provenance import file_sha256, toolchain_record
from agcws.policies import (EvolutionarySearch, HybridSearch, MutationSearch,
                            OfflineAgent, RandomSearch, VertexAgent)
from evaluate_aes_workload import evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--policy", choices=("random", "mutation", "evolutionary",
                                              "offline-agent", "offline-hybrid", "vertex"),
                        default="random")
    parser.add_argument("--target", type=float, default=0.5)
    # Keep the CLI default aligned with the pre-registered primary endpoint.
    # Sensitivity values must be selected explicitly.
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--p-min", type=float, required=True)
    parser.add_argument("--p-max", type=float, required=True)
    parser.add_argument("--budget", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("out/aes-search"))
    parser.add_argument("--fidelity", choices=("activity", "synthesis"), default="activity",
                        help="inner-loop oracle; use synthesis for finalist validation")
    parser.add_argument("--model", default=os.environ.get("AGCWS_GEMINI_MODEL"))
    parser.add_argument("--project", default=os.environ.get("AGCWS_GCP_PROJECT"))
    parser.add_argument("--prompt", type=Path, default=ROOT / "prompts/agent_system_v1.txt")
    args = parser.parse_args()
    policies = {"random": RandomSearch, "mutation": MutationSearch,
                "evolutionary": EvolutionarySearch, "offline-agent": OfflineAgent}
    if args.policy == "vertex":
        if not args.model or not args.project:
            parser.error("vertex policy requires --model/AGCWS_GEMINI_MODEL and --project/AGCWS_GCP_PROJECT")
        policy = VertexAgent.from_vertex(args.prompt.read_text(), model=args.model, project=args.project)
    elif args.policy == "offline-hybrid":
        agent = OfflineAgent(args.seed)
        policy = HybridSearch(agent.proposer, seed=args.seed,
                              model=agent.model, prompt_hash=agent.prompt_hash)
    else:
        policy = policies[args.policy](args.seed)
    counter = 0

    def evaluator(workload: dict) -> PowerProfile:
        nonlocal counter
        counter += 1
        workload_path = args.out / "workloads" / f"workload-{counter:05d}.json"
        workload_path.parent.mkdir(parents=True, exist_ok=True)
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        trial_dir = args.out / "evaluations" / f"trial-{counter:05d}"
        if args.fidelity == "activity":
            subprocess.run([sys.executable, "scripts/run_aes_workload.py",
                            str(workload_path), "--out", str(trial_dir)],
                           check=True, capture_output=True, text=True)
            log = (trial_dir / "run.log").read_text()
            match = re.search(r"AES_CORE_WORKLOAD_DONE blocks=(\d+)", log)
            if not match:
                raise RuntimeError("simulation log has no completed-work marker")
            activity = json.loads((trial_dir / "activity.json").read_text())
            edges = max(1, int(activity["clock_edges"]))
            return PowerProfile(
                mean_power=float(activity["total_transitions"]) / edges,
                peak_power=float(max(activity["per_cycle_toggles"] or [0])),
                per_cycle_toggles=tuple(activity["per_cycle_toggles"]),
                windowed=tuple(activity["window_toggles"]),
                useful_work=float(match.group(1)), valid=True, fidelity="activity",
                provenance={"oracle": "verilator-vcd",
                            "workload_sha256": file_sha256(workload_path),
                            "activity_sha256": file_sha256(trial_dir / "activity.json"),
                            "tools": toolchain_record({
                                "verilator": (config.VERILATOR, ("--version",)),
                            })})
        result = evaluate(workload_path, args.synthesis_dir, trial_dir, allow_invalid=True)
        if not result["valid"]:
            return PowerProfile(mean_power=0.0, peak_power=0.0,
                                useful_work=result["useful_work"], valid=False,
                                fidelity="synthesis", provenance={"invalid_stage": result["invalid_stage"],
                                                                    "invalid_reason": result["invalid_reason"]})
        return PowerProfile(mean_power=result["mean_power"], peak_power=result["mean_power"],
                            useful_work=result["useful_work"], valid=result["valid"],
                            fidelity="synthesis", provenance=result["provenance"])

    trials = run_search(AESAdapter(), policy, ScalarGoal(args.target, args.epsilon), evaluator,
                        budget=args.budget, batch_size=8, seed=args.seed,
                        p_min=args.p_min, p_max=args.p_max, output_dir=args.out)
    print(json.dumps({"policy": args.policy, "trials": len(trials), "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
