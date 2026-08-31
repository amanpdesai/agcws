#!/usr/bin/env python3
"""Freeze Slice-4 AES envelope and calibration parameters into JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.experiments.calibration import calibration_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path, help="corpus.jsonl from run_aes_random_corpus")
    parser.add_argument("--solved-fraction", type=float)
    parser.add_argument("--out", type=Path, default=Path("calibration.json"))
    args = parser.parse_args()
    records = [json.loads(line) for line in args.corpus.read_text().splitlines() if line.strip()]
    result = calibration_record(records, args.solved_fraction)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
