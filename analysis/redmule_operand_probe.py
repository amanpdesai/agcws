"""Fixed operand sweep for unresolved RedMulE requests; no target substitution."""

import argparse
import copy
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare
from agcws.pipeline.storage import read, write


def cases(reports):
    result = []
    for row in reports:
        result.append({"id": row["id"] + "-replay", "program": row["program"]})
        if row["qualified"]:
            continue
        for pattern in ("zeros", "alternating", "random"):
            for seed in range(16):
                program = copy.deepcopy(row["program"])
                program.update(pattern=pattern, data_seed=seed)
                result.append({"id": f"{row['id']}-{pattern}-{seed:02}", "program": program})
    return result


def plan(parent, destination):
    manifest = read(parent / "manifest.json")
    reports = read(parent / "complete.json")["reports"]
    if manifest["domain"] != "redmule-temporal" or len(reports) != 18:
        raise ValueError("complete RedMulE v4 panel required")
    proposals = cases(reports)
    if len(proposals) != 354:
        raise ValueError("expected seven unresolved requests and eighteen parent replays")
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "parent-manifest.json", manifest)
    write(destination / "parent-reports.json", reports)
    write(destination / "reference-spec.json", manifest["measurement"]["spec"])
    prepare(ROOT, destination / "reference-spec.json", destination / "reference")
    write(destination / "config.json", {"name": "redmule-operand-probe-v1", "domain": "redmule-temporal",
          "scope": "fixed CPU operand witness search; all attempts retained; no policy comparison",
          "cases": proposals, "max_workers": 18})
    runpy.run_path(ROOT / "scripts/probe_fixed_cases.py")["prepare"](
        destination / "reference", destination / "config.json", destination / "probe")
    return {"cases": len(proposals), "executed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    print(plan(args.parent, args.directory))
