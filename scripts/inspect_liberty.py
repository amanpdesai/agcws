#!/usr/bin/env python3
"""Report the characterization features required by R-01."""
import argparse
import hashlib
import json
import re
from pathlib import Path

def inspect(path: Path) -> dict:
    text = path.read_text(errors="replace")
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
        "internal_power_groups": len(re.findall(r"\binternal_power\s*\(", text)),
        "rise_power_tables": len(re.findall(r"\brise_power\s*\(", text)),
        "fall_power_tables": len(re.findall(r"\bfall_power\s*\(", text)),
        "cell_leakage_power": len(re.findall(r"\bcell_leakage_power\s*:", text)),
        "capacitance_entries": len(re.findall(r"\bcapacitance\s*[:(]", text)),
        "clock_gating_cells": len(re.findall(r"clock_gating_integrated_cell", text)),
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("liberty", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.liberty), indent=2))

if __name__ == "__main__":
    main()
