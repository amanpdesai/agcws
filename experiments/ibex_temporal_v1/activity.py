"""Streaming, core-scoped bit transitions in a fixed retired-marker window."""

import argparse
import json
import subprocess
import time
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v1.program import HORIZON

CORE = "TOP.ibex_simple_system.u_top.u_ibex_top.u_ibex_core"
CLOCK = "TOP.ibex_simple_system.u_top.clk_i"


def markers(trace, pcs):
    found = {}
    retired = 0
    with trace.open() as stream:
        next(stream)
        for line in stream:
            row = line.split()
            if len(row) < 4:
                raise ValueError("malformed retirement trace")
            tick, cycle, pc = int(row[0]), int(row[1]), int(row[2], 16)
            for name, address in pcs.items():
                if pc == address:
                    if name in found:
                        raise ValueError("measurement marker retired repeatedly")
                    found[name] = {"tick": tick, "cycle": cycle}
            retired += 1
    if found.keys() != pcs.keys():
        raise ValueError("missing measurement markers")
    return found, retired


def stream_activity(lines, begin, end):
    scope, selected, values = [], set(), {}
    clock = None
    clock_value = None
    edges, bins, previous_edge, period = 0, [0] * 8, None, None
    timestamp, header, unknowns = 0, True, 0
    last_tick = 0
    timescale = None
    scale_pending = False
    checked_initial_state = False
    for line in lines:
        if header:
            fields = line.split()
            if not fields:
                continue
            if fields[0] == "$timescale":
                scale_pending = True
                if len(fields) > 1:
                    timescale = fields[1]
            elif scale_pending:
                if fields[0] != "$end":
                    timescale = fields[0]
                else:
                    scale_pending = False
            if fields[0] == "$scope":
                scope.append(fields[2])
            elif fields[0] == "$upscope":
                scope.pop()
            elif fields[0] == "$var":
                identifier, name = fields[3], ".".join([*scope, fields[4]])
                if name == CLOCK:
                    clock = identifier
                if (
                    name.startswith(CORE + ".")
                    and ".cs_registers_i." not in name
                    and fields[1] != "parameter"
                ):
                    selected.add(identifier)
            elif fields[0] == "$enddefinitions":
                header = False
                if not selected or clock is None:
                    raise ValueError("missing declared core or clock")
                selected.discard(clock)
            continue
        if line.startswith("#"):
            timestamp = int(line[1:])
            last_tick = timestamp
            if timestamp >= begin and not checked_initial_state:
                if any(values.get(identifier) is None for identifier in selected):
                    raise ValueError("unknown carried state at measurement start")
                checked_initial_state = True
            continue
        if not line or line[0] in "$ \n":
            continue
        if line[0] == "b":
            value, identifier = line[1:].split()
        elif line[0] in "01xXzZ":
            value, identifier = line[0], line[1:].strip()
        else:
            continue
        if identifier == clock:
            if clock_value == "0" and value == "1":
                if previous_edge is not None:
                    delta = timestamp - previous_edge
                    if period is not None and period != delta:
                        raise ValueError("nonuniform clock")
                    period = delta
                previous_edge = timestamp
                if begin <= timestamp < end:
                    edges += 1
            clock_value = value
        if identifier not in selected:
            continue
        old = values.get(identifier)
        try:
            new = int(value, 2)
        except ValueError:
            if begin <= timestamp < end:
                unknowns += 1
            new = None
        if old is not None and new is not None and begin <= timestamp < end:
            bins[(timestamp - begin) * 8 // (end - begin)] += (old ^ new).bit_count()
        values[identifier] = new
    if edges != HORIZON or last_tick < end or period != 2 or unknowns:
        raise ValueError(
            f"invalid observation: edges={edges}, period={period}, unknowns={unknowns}"
        )
    return {
        "window_bit_transitions": bins,
        "window_rates": [x / (HORIZON / 8) for x in bins],
        "clock_edges": edges,
        "period_ticks": period,
        "begin_tick": begin,
        "end_tick": end,
        "timescale": timescale,
        "selected_identifiers": len(selected),
        "scope": CORE,
        "exclusions": ["clock", "cs_registers_i"],
        "unknown_events": unknowns,
        "units": "unique core-net bit transitions per clock edge; not watts",
    }


def extract(root):
    start = time.monotonic()
    functional = json.loads((root / "functional.json").read_text())
    found, retired = markers(root / "trace_core_00000000.log", functional["marker_pcs"])
    begin = found["measure_start"]["tick"]
    end = begin + 2 * HORIZON
    if not begin < found["body_complete"]["tick"] < end < found["measure_stop"]["tick"]:
        raise ValueError("useful work or observation window did not complete in time")
    with (
        (root / "activity-conversion.log").open("w") as errors,
        subprocess.Popen(
            ["fst2vcd", str(root / "sim.fst")],
            stdout=subprocess.PIPE,
            stderr=errors,
            text=True,
        ) as process,
    ):
        try:
            profile = stream_activity(process.stdout, begin, end)
        finally:
            process.stdout.close()
        if process.wait():
            raise ValueError("FST conversion failed")
    profile.update(
        markers=found,
        retired_instructions=retired,
        waveform_sha256=file_sha256(root / "sim.fst"),
        source_sha256=file_sha256(Path(__file__)),
        extraction_s=time.monotonic() - start,
    )
    (root / "profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    print(json.dumps(profile), flush=True)
    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    extract(parser.parse_args().root)
