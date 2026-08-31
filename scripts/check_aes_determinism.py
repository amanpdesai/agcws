#!/usr/bin/env python3
"""Check that repeated AES evaluations produce identical observable artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from scripts.evaluate_aes_workload import evaluate
except ModuleNotFoundError:  # direct execution: scripts/ is on sys.path
    from evaluate_aes_workload import evaluate


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", type=Path)
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-determinism"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    for index in range(2):
        result_dir = args.out / f"run-{index}"
        result = evaluate(args.workload, args.synthesis_dir, result_dir)
        results.append({"mean_power": result["mean_power"],
                        "useful_work": result["useful_work"],
                        "activity_sha256": digest(result_dir / "activity.json"),
                        "vcd_sha256": digest(result_dir / "activity.vcd")})
    if results[0] != results[1]:
        raise SystemExit(json.dumps({"deterministic": False, "runs": results}, indent=2))
    report = {"deterministic": True, "runs": results}
    (args.out / "determinism.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
