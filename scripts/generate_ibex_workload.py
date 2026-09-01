#!/usr/bin/env python3
"""Generate a deterministic floor-compliant Ibex workload."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def generate(instructions: int) -> dict:
    if instructions < 1:
        raise ValueError("instructions must be positive")
    return {"program": [{"op": "nop"} for _ in range(instructions)] + [{"op": "ecall"}]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--instructions", type=int, default=10_000)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(generate(args.instructions), indent=2) + "\n")


if __name__ == "__main__":
    main()
