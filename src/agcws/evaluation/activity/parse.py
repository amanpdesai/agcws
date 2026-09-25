#!/usr/bin/env python3
"""Extract transition counts and clock-bucketed activity from a VCD.

The default mode uses the generic value-change parser. The explicit
``--bit-cycles`` mode uses the benchmark's known-bit counter instead.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.evaluation.activity.generic import parse_vcd
from agcws.evaluation.activity.known_bits import Observation, read_bits


def parse(path: Path, clock_name: str = "clk_i", windows: int = 16) -> dict:
    """Compatibility wrapper for callers of the historical script API."""
    return parse_vcd(path, clock_name, windows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("vcd", type=Path)
    parser.add_argument("--clock", default="clk_i")
    parser.add_argument("--windows", type=int, default=16)
    parser.add_argument("--scope", default=None)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--bit-cycles", type=int, help="select known-bit-activity-v2 at this exact horizon")
    args = parser.parse_args()
    if args.bit_cycles is not None:
        if args.scope is None:
            parser.error("bit activity requires an explicit scope")
        result = read_bits(args.vcd, Observation(args.scope, args.clock, args.bit_cycles, args.windows))
    else:
        result = parse_vcd(args.vcd, args.clock, args.windows, scope_prefix=args.scope)
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end="")
