"""Predeclared coarse release-coordinate refinement, retaining rejected proposals."""

import argparse
import concurrent.futures
import copy
import fcntl
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.metrics import error
from agcws.pipeline.redmule import RedmuleTemporal
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import qualify

STEPS = (8192, 4096, 2048, 1024)


def proposals(program):
    rows = []
    for index in range(len(program["phases"])):
        for step in STEPS:
            for sign in (-1, 1):
                candidate = copy.deepcopy(program)
                candidate["phases"][index]["start"] += sign*step
                rows.append(candidate)
    return rows


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan(parent, root):
    m = read(parent / "manifest.json")
    reports = read(parent / "complete.json")["reports"]
    if m["domain"] != "redmule-temporal" or len(reports) != 18:
        raise ValueError("complete RedMulE v4 parent required")
    root.mkdir(parents=True, exist_ok=False)
    write(root / "spec.json", m["measurement"]["spec"])
    prepare(ROOT, root / "spec.json", root / "run")
    write(root / "config.json", {"bank": m["bank"], "parents": reports, "rounds": 4,
                                 "steps": list(STEPS), "max_workers": 18})
    write(root / "freeze.json", {"config": digest(root / "config.json"), "driver": digest(Path(__file__))})
    return {"cases": 18, "rounds_maximum": 4, "executed": False}


def run(root):
    if read(root / "freeze.json") != {"config": digest(root / "config.json"), "driver": digest(Path(__file__))}:
        raise ValueError("frozen procedure changed")
    config = read(root / "config.json")
    manifest = verify_inputs(ROOT, root / "run")
    design = RedmuleTemporal()
    scale = config["bank"]["calibration"]["scale"]
    requests = {f"{s}-{r['id']}": r for s, p in config["bank"]["splits"].items() for r in p["requests"]}

    def measure(program):
        result, _ = design.measured(program, root / "run", manifest)
        return {"program": program, "measurement": result}

    def loss(row, request):
        return error(row["measurement"]["rates"], request["rates"], scale) if row["measurement"]["valid"] else float("inf")

    reports = []
    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
            for parent in config["parents"]:
                name = parent["id"]
                request = requests[name]
                best = measure(parent["program"])
                ensure(root / "run/panel" / name / "initial.json", best)
                if any(best["measurement"].get(k) != parent["measurement"].get(k) for k in ("valid", "rates", "profile")):
                    raise ValueError("parent replay changed")
                slots = 1
                for index in range(4):
                    admission = qualify(request, best["measurement"], scale=scale, tolerance=.1, nonflat_margin=.02)
                    if admission["qualified"]:
                        break
                    path = root / "run/panel" / name / f"round-{index}.json"
                    programs = proposals(best["program"])
                    if path.exists():
                        rows = read(path)
                        if [r["program"] for r in rows] != programs:
                            raise ValueError("resumed proposals differ")
                        for row in rows:
                            if measure(row["program"]) != row:
                                raise ValueError("resumed measurement differs")
                    else:
                        rows = list(pool.map(measure, programs))
                        ensure(path, rows)
                    slots += len(rows)
                    best = min([best, *rows], key=lambda row: loss(row, request))
                    print({"case": name, "round": index, "slots": slots, "error": loss(best, request)}, flush=True)
                report = {"id": name, "charged_slots": slots, **best,
                          **qualify(request, best["measurement"], scale=scale, tolerance=.1, nonflat_margin=.02)}
                ensure(root / "run/panel" / name / "complete.json", report)
                reports.append(report)
        ensure(root / "run/complete.json", {"reports": reports, "charged_slots": sum(r["charged_slots"] for r in reports)})
    return {"qualified": sum(r["qualified"] for r in reports), "cases": len(reports)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    parser.add_argument("--parent", type=Path)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        if args.parent is None:
            parser.error("parent required")
        print(plan(args.parent, args.directory))
    else:
        if not args.execute:
            parser.error("execute required")
        print(run(args.directory))
