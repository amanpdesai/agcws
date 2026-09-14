"""Summarize queued-job timing without assuming independent additive pulses."""

import argparse
import hashlib
from pathlib import Path

from agcws.pipeline.storage import read, write


def summarize(root):
    complete = read(root / "complete.json")
    if complete["charged_slots"] != 18 or complete["valid"] != 18:
        raise ValueError("all eighteen frozen diagnostic cases must complete validly")
    rows = []
    for case in complete["results"]:
        measurement, program = case["measurement"], case["program"]
        attempts = list((root / "cache" / measurement["cache_id"]).glob("attempt-*/functional.json"))
        if len(attempts) != 1:
            raise ValueError("one functional record required")
        functional = read(attempts[0])
        activity = read(attempts[0].with_name("activity.json"))
        completions = functional["job_completions"]
        expected = sum(phase["jobs"] for phase in program["phases"])
        if (not functional["valid"] or functional["completed_jobs"] != expected
                or len(completions) != expected or activity["clock_edges"] != 262144):
            raise ValueError("functional count or observation window differs")
        times = [row[1] for row in completions]
        gaps = [right-left for left, right in zip(times, times[1:])]
        if any(gap <= 0 for gap in gaps) or times[-1] >= activity["clock_edges"]:
            raise ValueError("completion timestamps must be ordered inside the window")
        rows.append({"id": case["id"], "program": program,
                     "release_to_first_completion_cycles": times[0]-program["phases"][0]["start"],
                     "inter_completion_cycles": gaps, "last_completion_cycle": times[-1],
                     "rates": measurement["rates"], "useful_work": functional["useful_work"],
                     "cache_id": measurement["cache_id"]})
    return {"scope": "target-independent queued-job diagnostic, not target qualification",
            "manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
            "complete_sha256": hashlib.sha256((root / "complete.json").read_bytes()).hexdigest(),
            "cases": rows, "full_study_ready": False,
            "caution": "Completion intervals include software/queue overhead; they are not isolated hardware service times."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, summarize(args.directory))
