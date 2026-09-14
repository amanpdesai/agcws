"""Declared concurrency/timing corners before choosing a replacement DMA window."""

import argparse
from pathlib import Path

from agcws.pipeline.storage import write
from agcws.workloads.schedule import ScheduleContract, expand_schedule


def config():
    cases = []
    for depth in (1, 2, 4, 8):
        groups = 64//depth
        for timing in ("before", "after", "distributed"):
            sequence = []
            if timing == "before":
                sequence.append({"op": "wait", "cycles": 6000})
            for i in range(groups):
                if timing == "distributed":
                    sequence.append({"op": "wait", "cycles": (i+1)*6000//groups-i*6000//groups})
                sequence.append({"op": "work", "units": depth})
            if timing == "after":
                sequence.append({"op": "wait", "cycles": 6000})
            program = {"sequence": sequence}
            expand_schedule(program, ScheduleContract(64, 6000))
            cases.append({"id": f"depth-{depth}-{timing}", "program": program})
    return {"name": "dma-timing-corners-v1", "domain": "dma-temporal", "max_workers": 12,
            "scope": "Fixed CPU timing diagnostic, not policy comparison or target admission",
            "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, config())
