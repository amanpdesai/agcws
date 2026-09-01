#!/usr/bin/env python3
"""Write the portable result record for one Ibex simulation artifact."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from agcws.provenance import input_record, toolchain_record

USEFUL_WORK_FLOOR = 10_000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("workload", type=Path)
    args = parser.parse_args()
    counters = {}
    with (args.artifact / "ibex_simple_system_pcount.csv").open(newline="") as stream:
        for row in csv.reader(stream):
            if len(row) == 2:
                counters[row[0]] = int(row[1])
    useful_work = counters.get("Instructions Retired", 0)
    inputs = {"workload": args.artifact / "workload.json",
              "waveform": args.artifact / "activity.vcd" if (args.artifact / "activity.vcd").is_file()
              else args.artifact / "sim.fst",
              "performance_counters": args.artifact / "ibex_simple_system_pcount.csv"}
    (args.artifact / "result.json").write_text(json.dumps({
        "valid": useful_work >= USEFUL_WORK_FLOOR,
        "useful_work_floor": USEFUL_WORK_FLOOR,
        "useful_work": useful_work,
        "counters": counters,
        "provenance": {
            "inputs": input_record(inputs),
            "tools": toolchain_record({
                "verilator": (os.environ.get("AGCWS_VERILATOR", "verilator"), ("--version",)),
                "riscv_gcc": (os.environ.get("AGCWS_RISCV_GCC", "riscv64-unknown-elf-gcc"), ("--version",)),
            }),
        },
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
