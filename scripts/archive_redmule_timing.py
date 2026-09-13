"""Archive the reference-checked RedMulE timing gate, not a benchmark result."""

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

from agcws.pipeline.storage import write


def checked_case(directory, activity_name):
    activity = json.loads((directory / activity_name).read_text())
    log = (directory / "run.log").read_text()
    if "AGCWS_REDMULE_WINDOW_DONE cycles=65536" not in log or "[TB] - errors=00000000" not in log:
        raise ValueError("missing successful fixed-window reference check")
    counts = activity["per_cycle_toggles"]
    if activity["clock_edges"] != 65536 or len(counts) != 65536:
        raise ValueError("waveform clock does not match the observed window")
    jobs = [{"job": int(job), "cycle": int(cycle), "errors": int(errors)}
            for job, cycle, errors in re.findall(r"AGCWS_REDMULE_JOB job=(\d+) cycle=(\d+) errors=(\d+)", log)]
    if any(job["errors"] or job["cycle"] >= 65536 for job in jobs):
        raise ValueError("job failed or completed outside observation window")
    return {"activity": activity, "run_log": log, "jobs": jobs,
            "window_rates": [sum(counts[i*8192:(i+1)*8192])/8192 for i in range(8)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--scheduled", type=Path, required=True)
    parser.add_argument("--negative", type=Path, required=True)
    parser.add_argument("--reference-inputs", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    reference = checked_case(args.harness / "reference", "activity_qualified.json")
    scheduled = checked_case(args.scheduled / "replay", "activity.json")
    if [job["job"] for job in scheduled["jobs"]] != [0, 1, 2]:
        raise ValueError("three sequential checked jobs required")
    negative = (args.negative / "run.log").read_text()
    if "REDMULE_INCOMPLETE" not in negative or "AGCWS_REDMULE_WINDOW_DONE" in negative:
        raise ValueError("unfinished-work rejection was not observed")
    record = {
        "status": "engineering timing gate; not a qualified target or shared-backend smoke",
        "source_commit": args.source_commit, "image": args.image,
        "scope": "redmule_tb_wrap.i_redmule_tb.i_redmule_wrap", "clock": "redmule_tb_wrap.clk",
        "window": "65536 continuous clock edges including reset; eight equal bins",
        "derivation": json.loads((args.harness / "derivation.json").read_text()),
        "reference_headers": {path.name: path.read_text() for path in sorted((args.reference_inputs / "inc").glob("*.h"))},
        "scheduled_header": (args.scheduled / "workload.h").read_text(),
        "cases": {"single_job": reference, "scheduled_three_jobs": scheduled},
        "negative": {"run_log": negative, "activity_scored": False},
        "rejected_unqualified_clock_edges": json.loads((args.harness / "reference/activity.json").read_text())["clock_edges"],
    }
    blob = gzip.compress(json.dumps(record, sort_keys=True, allow_nan=False).encode(), mtime=0)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "evidence.json.gz").write_bytes(blob)
    write(args.out / "summary.json", {
        "status": record["status"], "sha256": hashlib.sha256(blob).hexdigest(),
        "source_commit": args.source_commit, "scope": record["scope"], "clock": record["clock"],
        "clock_edges": 65536, "rejected_unqualified_clock_edges": record["rejected_unqualified_clock_edges"],
        "cases": {name: {"window_rates": case["window_rates"], "jobs": case["jobs"]}
                  for name, case in record["cases"].items()}, "unfinished_work_rejected": True,
    })


if __name__ == "__main__":
    main()
