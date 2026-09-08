"""Read immutable checkpoints without presenting partial runs as an aggregate."""

import argparse
import collections
import datetime
import json
from pathlib import Path

from experiments.ibex_depth_v1.storage import read


def status(root):
    counts = collections.Counter()
    stages = collections.Counter()
    known_cost, unknown = 0.0, 0
    api_errors = []
    for path in root.glob("panel/*/*/*/batches/*/trials.json"):
        arm = path.parents[2].name
        rows = read(path)
        counts[arm] += len(rows)
        stages.update("VALID" if t["valid"] else t["stage"] for t in rows)
    for path in root.glob("panel/*/*/*/batches/*/response.json"):
        response = read(path)
        if response["usage_unknown"]:
            unknown += 1
        else:
            known_cost += response["estimated_usd"]
        if response.get("api_error"):
            api_errors.append(
                {
                    "batch": str(path.parent.relative_to(root)),
                    "error": response["api_error"],
                }
            )
    unresolved = [
        str(p.relative_to(root))
        for p in root.glob("panel/*/*/*/batches/*/request_started.json")
        if not (p.parent / "response.json").exists()
    ]
    return {
        "snapshot_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "phase": "execution-status-not-comparative-inference",
        "completed_slots_by_arm": dict(counts),
        "validity": dict(stages),
        "complete_prefixes": [
            n for n in (16, 64, 128) if (root / f"prefix-{n}-complete.json").exists()
        ],
        "known_estimated_usd": known_cost,
        "unknown_usage_calls": unknown,
        "api_errors": api_errors,
        "in_flight_or_unresolved_requests": unresolved,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contents = json.dumps(status(args.root), indent=2) + "\n"
    if args.output:
        args.output.write_text(contents)
    print(contents, end="")
