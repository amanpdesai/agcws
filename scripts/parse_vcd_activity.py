#!/usr/bin/env python3
"""Extract transition counts and clock-bucketed activity from a VCD.

The implementation lives in :mod:`agcws.nodes.activity`; keeping this command
as a thin wrapper ensures scripts and CHIA nodes produce identical artifacts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The command is also called from shell-based simulator harnesses, where the
# package may not be installed in the active interpreter.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.nodes.activity import parse_vcd


def parse(path: Path, clock_name: str = "clk_i", windows: int = 16) -> dict:
    """Compatibility wrapper for callers of the historical script API."""
    return parse_vcd(path, clock_name, windows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("vcd", type=Path)
    parser.add_argument("--clock", default="clk_i")
    parser.add_argument("--windows", type=int, default=16)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = parse(args.vcd, args.clock, args.windows)
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end="")
