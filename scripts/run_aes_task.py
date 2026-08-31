#!/usr/bin/env python3
"""Run or resume one content-addressed AES evaluation task."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.tasks import TaskStore, file_digest
from evaluate_aes_workload import evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", type=Path)
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-tasks"))
    args = parser.parse_args()
    manifest = args.synthesis_dir / "manifest.json"
    if not manifest.exists():
        raise FileNotFoundError(f"missing synthesis manifest: {manifest}")
    inputs = {
        "workload_sha256": file_digest(args.workload),
        "synthesis_manifest_sha256": file_digest(manifest),
        "evaluator": "aes-opensta-v1",
    }
    store = TaskStore(args.out)

    def action(output: Path) -> None:
        evaluate(args.workload, args.synthesis_dir, output)
        (output / "task_inputs.json").write_text(
            json.dumps(inputs, indent=2, sort_keys=True) + "\n"
        )

    task = store.run("evaluate", inputs, action)
    result_path = task.output_dir / "result.json"
    if not result_path.exists():
        raise RuntimeError(f"task completed without result: {result_path}")
    result = json.loads(result_path.read_text())
    result["task"] = {"name": task.name, "key": task.key, "cached": task.cached,
                      "manifest": str(task.manifest.resolve())}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
