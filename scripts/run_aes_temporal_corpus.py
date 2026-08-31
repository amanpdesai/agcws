#!/usr/bin/env python3
"""Evaluate deterministic AES schedules for temporal-profile calibration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.tasks import TaskStore, file_digest
try:
    from scripts.evaluate_aes_workload import evaluate
except ModuleNotFoundError:  # direct execution: scripts/ is on sys.path
    from evaluate_aes_workload import evaluate


def schedule_workload(name: str, blocks: int = 8) -> dict:
    if blocks < 2:
        raise ValueError("temporal schedules require at least two blocks")
    schedules = {
        "low_high_low": [0, 80, 0, 80, 0, 80, 0],
        "high_low_high": [80, 0, 80, 0, 80, 0, 80],
        "burst": [0] * (blocks - 1),
        # Keep the total idle interval below run_aes_workload's 10k-cycle cap.
        "ramp": [5 * index for index in range(blocks - 1)],
    }
    if name not in schedules:
        raise ValueError(f"unknown schedule: {name}")
    gaps = schedules[name]
    if len(gaps) != blocks - 1:
        gaps = (gaps * blocks)[:blocks - 1]
    operations: list[dict] = [{"op": "configure"}]
    for index in range(blocks):
        operations.append({"op": "encrypt", "blocks": 1})
        if index < len(gaps) and gaps[index]:
            operations.append({"op": "idle", "cycles": gaps[index]})
    return {"operations": operations, "data_pattern": 2}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-temporal-corpus"))
    parser.add_argument("--blocks", type=int, default=48)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = args.synthesis_dir / "manifest.json"
    if not manifest.exists():
        raise FileNotFoundError(f"missing synthesis manifest: {manifest}")
    store = TaskStore(args.out / "tasks")
    records = []
    for name in ("low_high_low", "high_low_high", "burst", "ramp"):
        workload = schedule_workload(name, args.blocks)
        workload_path = args.out / f"{name}.json"
        workload_path.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        inputs = {"workload_sha256": file_digest(workload_path),
                  "synthesis_manifest_sha256": file_digest(manifest),
                  "evaluator": "aes-opensta-v1"}

        def action(output: Path, workload_path=workload_path) -> None:
            evaluate(workload_path, args.synthesis_dir, output)

        task = store.run("evaluate", inputs, action,
                         required_outputs=("result.json", "activity.json"))
        result = json.loads((task.output_dir / "result.json").read_text())
        activity = result["activity"]
        peak = max(activity["window_toggles"] or [1])
        records.append({"name": name, "workload": workload, "task_key": task.key,
                        "cached": task.cached, "useful_work": result["useful_work"],
                        "mean_power": result["mean_power"],
                        "per_cycle_toggles": activity["per_cycle_toggles"],
                        "window_toggles": activity["window_toggles"],
                        "normalized_windows": [v / peak for v in activity["window_toggles"]]})
    (args.out / "corpus.jsonl").write_text("\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n")
    (args.out / "summary.json").write_text(json.dumps({"blocks": args.blocks,
        "schedules": [r["name"] for r in records], "record_count": len(records)}, indent=2) + "\n")
    print(json.dumps(json.loads((args.out / "summary.json").read_text()), indent=2))


if __name__ == "__main__":
    main()
