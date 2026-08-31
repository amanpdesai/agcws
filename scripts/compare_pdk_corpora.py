#!/usr/bin/env python3
"""Compare two JSONL power corpora by canonical workload identity."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.analysis.rank_agreement import rank_agreement, workload_id


def load(path: Path) -> list[tuple[str, float]]:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return [(workload_id(record["workload"]), float(record["mean_power"])) for record in records]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = rank_agreement(load(args.left), load(args.right))
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
