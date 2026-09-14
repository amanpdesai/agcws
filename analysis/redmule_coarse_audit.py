"""Recompute frozen coarse-search proposals, parent choices and qualification."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import error
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def audit(root):
    config = read(root / "config.json")
    if read(root / "freeze.json") != {
        "config": hashlib.sha256((root / "config.json").read_bytes()).hexdigest(),
        "driver": hashlib.sha256((ROOT / "analysis/redmule_coarse_timing.py").read_bytes()).hexdigest(),
    }:
        raise ValueError("frozen coarse protocol changed")
    verify_inputs(ROOT, root / "run")
    propose = runpy.run_path(ROOT / "analysis/redmule_coarse_timing.py")["proposals"]
    scale = config["bank"]["calibration"]["scale"]
    requests = {f"{s}-{r['id']}": r for s, p in config["bank"]["splits"].items() for r in p["requests"]}
    reports = []
    for parent in config["parents"]:
        name = parent["id"]
        request = requests[name]
        directory = root / "run/panel" / name
        best = read(directory / "initial.json")
        if best["program"] != parent["program"] or any(best["measurement"].get(k) != parent["measurement"].get(k) for k in ("valid", "rates", "profile")):
            raise ValueError("parent replay differs")

        def loss(row):
            return error(row["measurement"]["rates"], request["rates"], scale) if row["measurement"]["valid"] else float("inf")

        slots = 1
        paths = sorted(directory.glob("round-*.json"))
        if len(paths) > 4:
            raise ValueError("round budget exceeded")
        for index, path in enumerate(paths):
            if path.name != f"round-{index}.json" or qualify(request, best["measurement"], scale=scale, tolerance=.1, nonflat_margin=.02)["qualified"]:
                raise ValueError("round ordering or stopping differs")
            rows = read(path)
            if [r["program"] for r in rows] != propose(best["program"]):
                raise ValueError("generated round differs")
            for row in rows:
                result = row["measurement"]
                if result["valid"]:
                    if read(root / "run/cache" / result["cache_id"] / "result.json") != result:
                        raise ValueError("cached measurement differs")
                    if result["rates"] != result["profile"]["window_rates"] or result["profile"]["clock_edges"] != 65536:
                        raise ValueError("profile contract differs")
                elif result.get("rates") is not None:
                    raise ValueError("invalid proposal scored")
            slots += len(rows)
            best = min([best, *rows], key=loss)
        admission = qualify(request, best["measurement"], scale=scale, tolerance=.1, nonflat_margin=.02)
        if not admission["qualified"] and len(paths) != 4:
            raise ValueError("unqualified request stopped early")
        report = {"id": name, "charged_slots": slots, **best, **admission}
        if read(directory / "complete.json") != report:
            raise ValueError("case summary differs")
        reports.append(report)
    terminal = {"reports": reports, "charged_slots": sum(r["charged_slots"] for r in reports)}
    if read(root / "run/complete.json") != terminal:
        raise ValueError("terminal panel differs")
    return {"scope": "proposal, selection, cache and accounting replay; not independent simulation",
            "cases": len(reports), "charged_slots": terminal["charged_slots"],
            "qualified": sum(r["qualified"] for r in reports), "reports": [
                {k: r[k] for k in ("id", "qualified", "charged_slots", "witness_error")} for r in reports]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, audit(args.directory))
