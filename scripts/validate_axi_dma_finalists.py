#!/usr/bin/env python3
"""Validate DMA search finalists through coupled simulation and OpenSTA."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def finalists(path: Path, top_k: int) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    valid = [row for row in rows if row.get("validity", {}).get("valid")
             and row.get("loss") is not None]
    return sorted(valid, key=lambda row: float(row["loss"]))[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trials", type=Path)
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    records = []
    for index, trial in enumerate(finalists(args.trials, args.top_k)):
        workload = args.out / f"finalist-{index:03d}.json"
        workload.write_text(json.dumps(trial["workload"], indent=2, sort_keys=True) + "\n")
        sim_dir = args.out / f"simulation-{index:03d}"
        subprocess.run(["bash", "scripts/run_axi_dma_coupled.sh", str(workload), str(sim_dir)],
                       check=True)
        useful_work = sum(int(item["length"]) for item in trial["workload"]["transfers"])
        sta_dir = args.out / f"opensta-{index:03d}"
        subprocess.run(["bash", "scripts/run_opensta_axi_dma.sh", str(args.synthesis_dir),
                        str(sim_dir / "activity.vcd"), str(sta_dir), str(useful_work)], check=True)
        records.append({"rank": index + 1, "trial_id": trial.get("trial_id"),
                        "search_loss": trial["loss"],
                        "result": json.loads((sta_dir / "result.json").read_text())})
    (args.out / "validation.json").write_text(json.dumps({
        "fidelity": "synthesis", "source_trials": str(args.trials),
        "top_k": args.top_k, "finalists": records,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validated": len(records), "output": str(args.out.resolve())}, indent=2))


if __name__ == "__main__":
    main()
