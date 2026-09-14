"""Read accepted RedMulE trigger writes from existing VCDs, without resimulation."""

import argparse
from pathlib import Path

from agcws.pipeline.storage import read, write


def triggers(path):
    scope, codes, values = [], {}, {}
    wanted = {"clk_i", "data_req", "data_gnt", "data_we", "data_addr"}
    previous, edges, found = {}, 0, []

    def sample():
        nonlocal previous, edges
        if previous.get("clk_i") == "0" and values.get("clk_i") == "1":
            edges += 1
            # Transactions sample setup values, not post-edge CPU outputs.
            if all(previous.get(k) == "1" for k in ("data_req", "data_gnt", "data_we")):
                address = previous.get("data_addr", "x")
                if set(address) <= {"0", "1"} and int(address, 2) == 0x100000:
                    found.append(edges)
        previous = values.copy()

    with path.open() as stream:
        for line in stream:
            words = line.split()
            if words[:1] == ["$scope"]:
                scope.append(words[2])
            elif words[:1] == ["$upscope"]:
                scope.pop()
            elif words[:1] == ["$var"] and scope == ["redmule_tb_wrap", "i_redmule_tb"]:
                if words[4] in wanted:
                    codes[words[3]] = words[4]
            elif words[:1] == ["$enddefinitions"]:
                break
        if set(codes.values()) != wanted:
            raise ValueError("exact timing harness bus signals required")
        for line in stream:
            if line.startswith("#"):
                sample()
            elif line.startswith("b"):
                value, code = line[1:].split()
                if code in codes:
                    values[codes[code]] = value
            elif line[:1] in ("0", "1", "x", "z"):
                code = line[1:].strip()
                if code in codes:
                    values[codes[code]] = line[0]
        sample()
    return {"clock_edges": edges, "accepted_trigger_edges": found}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for case in read(args.directory / "complete.json")["results"]:
        if not case["id"].startswith("size16-alternating"):
            continue
        attempt = args.directory / "cache" / case["measurement"]["cache_id"] / "attempt-001"
        record = triggers(attempt / "activity.vcd")
        functional = read(attempt / "functional.json")
        if len(record["accepted_trigger_edges"]) != functional["completed_jobs"]:
            raise ValueError("accepted trigger count differs from completed jobs")
        rows.append({"id": case["id"], **record, "completions": functional["job_completions"]})
    write(args.output, {"scope": "post-hoc timing diagnosis, two size16 alternating cases", "cases": rows})
