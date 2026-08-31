#!/usr/bin/env python3
"""Extract transition counts and clock-bucketed activity from a VCD."""
from __future__ import annotations
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

VAR_RE = re.compile(r"\$var\s+\S+\s+(\d+)\s+(\S+)\s+(.+?)\s+\$end")

def parse(path: Path, clock_name: str = "clk_i", windows: int = 16) -> dict:
    ids: dict[str, tuple[str, int]] = {}
    clock_ids: set[str] = set()
    values: dict[str, str] = {}
    transitions: defaultdict[str, int] = defaultdict(int)
    per_time: defaultdict[int, int] = defaultdict(int)
    clock_edges: list[int] = []
    time = 0
    in_header = True
    for line in path.read_text(errors="replace").splitlines():
        match = VAR_RE.search(line) if in_header else None
        if match:
            width, identifier, name = int(match.group(1)), match.group(2), match.group(3)
            ids[identifier] = (name, width)
            if name.split()[-1] == clock_name:
                clock_ids.add(identifier)
            continue
        if line.startswith("$enddefinitions"):
            in_header = False
            continue
        if line.startswith("#"):
            time = int(line[1:])
            continue
        if not line or line[0] in "$ ":
            continue
        identifier: str
        value: str
        if line[0] in "01xXzZ":
            value, identifier = line[0], line[1:]
        elif line[0] == "b":
            value, identifier = line.split(maxsplit=1)
        else:
            continue
        old = values.get(identifier)
        if old is not None and old != value:
            name = ids.get(identifier, (identifier, 1))[0]
            transitions[name] += 1
            per_time[time] += 1
        values[identifier] = value
        if identifier in clock_ids and old == "0" and value == "1":
            clock_edges.append(time)
    if not clock_edges:
        clock_edges = sorted(per_time)
    buckets = [0] * min(windows, max(1, len(clock_edges)))
    if clock_edges:
        edge_set = {edge: index for index, edge in enumerate(clock_edges)}
        for timestamp, count in per_time.items():
            prior = [edge for edge in edge_set if edge <= timestamp]
            if prior:
                index = edge_set[max(prior)] * len(buckets) // len(clock_edges)
                buckets[min(index, len(buckets) - 1)] += count
    return {"vcd": str(path), "clock": clock_name, "clock_edges": len(clock_edges), "total_transitions": sum(transitions.values()), "signal_transitions": dict(sorted(transitions.items())), "window_toggles": buckets}

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
