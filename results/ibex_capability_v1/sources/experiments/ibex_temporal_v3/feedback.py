"""Retirement diagnostics aligned to the unchanged activity interval."""

import json
from pathlib import Path

from experiments.ibex_temporal_v1.activity import markers
from experiments.ibex_temporal_v3.program import HORIZON

CLASSES = (
    "alu",
    "multiply",
    "divide",
    "load",
    "store",
    "branch",
    "jump",
    "csr",
    "other",
)


def instruction_class(word):
    opcode, funct3, funct7 = word & 127, (word >> 12) & 7, (word >> 25) & 127
    if word & 3 != 3:
        raise ValueError("compressed instruction outside pinned RV32IM measurement")
    if opcode == 0x33 and funct7 == 1:
        return "multiply" if funct3 < 4 else "divide"
    if opcode == 0x73 and funct3 != 0:
        return "csr"
    return {
        0x03: "load",
        0x23: "store",
        0x63: "branch",
        0x6F: "jump",
        0x67: "jump",
        0x33: "alu",
        0x13: "alu",
        0x17: "alu",
        0x37: "alu",
    }.get(opcode, "other")


def retirement_bins(lines, begin, end):
    if end - begin != 2 * HORIZON:
        raise ValueError("fixed 200000-cycle interval required")
    counts = [{name: 0 for name in CLASSES} for _ in range(8)]
    previous, first_tick = None, None
    for line in lines:
        row = line.split()
        if len(row) < 4:
            raise ValueError("malformed retirement trace")
        tick, cycle = int(row[0]), int(row[1])
        if first_tick is None:
            first_tick = tick
        if previous is not None:
            dt, dc = tick - previous[0], cycle - previous[1]
            if dc <= 0 or dt != 2 * dc:
                raise ValueError("retirement clock mapping or order changed")
        previous = (tick, cycle)
        if begin <= tick < end:
            index = (tick - begin) * 8 // (end - begin)
            counts[index][instruction_class(int(row[3], 16))] += 1
    if first_tick is None or first_tick > begin or previous[0] < end:
        raise ValueError("retirement trace does not cover observation interval")
    totals = [sum(c.values()) for c in counts]
    return {
        "begin_tick": begin,
        "end_tick": end,
        "cycles_per_bin": HORIZON // 8,
        "retired_classes": counts,
        "retired_per_bin": totals,
        "cycles_without_retirement": [HORIZON // 8 - n for n in totals],
        "interpretation": "includes polling/control overhead; gaps are not attributed stall causes",
    }


def extract(root):
    functional = json.loads((root / "functional.json").read_text())
    trace = root / "trace_core_00000000.log"
    found, _ = markers(trace, functional["marker_pcs"])
    begin = found["measure_start"]["tick"]
    with trace.open() as stream:
        next(stream)
        result = retirement_bins(stream, begin, begin + 2 * HORIZON)
    elapsed = (found["body_complete"]["tick"] - begin) // 2
    result.update(
        body_completion_cycles=elapsed,
        body_overrun_cycles=max(0, elapsed - HORIZON),
        body_completed_before_deadline=0 < elapsed < HORIZON,
        deadline_margin_cycles=HORIZON - elapsed,
        allocation=functional["expected"]["allocation"],
        trace_file=str(Path("trace_core_00000000.log")),
    )
    return result
