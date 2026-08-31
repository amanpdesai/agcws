#!/usr/bin/env python3
"""Aggregate runner summaries found below a directory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.analysis.aggregate import aggregate_summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="+",
                        help="one or more directories containing summary.json files")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    records = []
    for root in args.root:
        for path in sorted(root.rglob("summary.json")):
            record = json.loads(path.read_text())
            # Preserve the run identity when the summary itself came from the
            # generic runner, which intentionally stores no filesystem paths.
            record.setdefault("run_dir", str(path.parent.relative_to(root)))
            record.setdefault("source_root", str(root))
            records.append(record)
    result = aggregate_summaries(records)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
