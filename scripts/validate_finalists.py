#!/usr/bin/env python3
"""Re-evaluate search finalists at synthesis fidelity without rewriting trials."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.evaluate_aes_workload import evaluate


def select_finalists(trials_path: Path, top_k: int) -> list[dict]:
    if top_k <= 0:
        raise ValueError("top-k must be positive")
    trials = [json.loads(line) for line in trials_path.read_text().splitlines() if line.strip()]
    valid = [trial for trial in trials if trial.get("validity", {}).get("valid")
             and trial.get("loss") is not None]
    return sorted(valid, key=lambda trial: float(trial["loss"]))[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trials", type=Path)
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    finalists = select_finalists(args.trials, args.top_k)
    results = []
    for index, trial in enumerate(finalists):
        workload_path = args.out / f"finalist-{index:03d}.json"
        workload_path.write_text(json.dumps(trial["workload"], indent=2, sort_keys=True) + "\n")
        result = evaluate(workload_path, args.synthesis_dir,
                          args.out / f"evaluation-{index:03d}")
        results.append({"rank": index + 1, "search_loss": trial["loss"],
                        "trial_id": trial.get("trial_id"), "result": result})
    payload = {"source_trials": str(args.trials), "fidelity": "synthesis",
               "top_k": args.top_k, "finalists": results}
    (args.out / "validation.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validated": len(results), "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
