#!/usr/bin/env python3
"""Compare synthesized cell usage with cells defined by a Liberty file."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def liberty_cells(path: Path) -> set[str]:
    text = path.read_text(errors="replace")
    return set(re.findall(r"\bcell\s*\(\s*\"?([^\s\)\"]+)", text))


def cell_histogram(path: Path) -> dict[str, int]:
    data = json.loads(path.read_text())
    modules = data.get("modules", {})
    histogram: dict[str, int] = {}
    for module in modules.values():
        for name, count in module.get("num_cells_by_type", {}).items():
            clean = name.lstrip("\\")
            histogram[clean] = histogram.get(clean, 0) + int(count)
    return histogram


def inspect(stat_path: Path, liberty_path: Path) -> dict:
    histogram = cell_histogram(stat_path)
    defined = liberty_cells(liberty_path)
    matched = {name: count for name, count in histogram.items() if name in defined}
    instances = sum(histogram.values())
    matched_instances = sum(matched.values())
    return {
        "stat": str(stat_path),
        "liberty": str(liberty_path),
        "distinct_netlist_cells": len(histogram),
        "distinct_cells_defined": len(defined),
        "distinct_cells_matched": len(matched),
        "netlist_cell_instances": instances,
        "matched_cell_instances": matched_instances,
        "instance_coverage": matched_instances / instances if instances else 0.0,
        "unmatched_cells": sorted(set(histogram) - defined),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stat", type=Path, help="Yosys stat.json")
    parser.add_argument("liberty", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.stat, args.liberty), indent=2))


if __name__ == "__main__":
    main()
