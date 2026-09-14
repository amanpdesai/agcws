"""Streaming, core-scoped bit transitions in a fixed retired-marker window."""

import argparse
import json
import subprocess
import time
from pathlib import Path

from agcws.nodes.bit_activity import Observation, stream_bits
from agcws.pipeline.ibex.program import HORIZON
from agcws.provenance import file_sha256

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
    result = stream_bits(lines, Observation(CORE, CLOCK, HORIZON, begin=begin, end=end,
                                           exclusions=(".cs_registers_i.",),
                                           require_known_initial=True, period=2))
    result.pop("per_cycle_toggles")
    return {**result, "unknown_events": 0}


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
