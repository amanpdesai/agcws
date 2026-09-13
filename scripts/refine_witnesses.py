"""CPU-only local witness refinement; shared evaluator, immutable paired feedback."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import error
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import qualify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    return {str(p.relative_to(ROOT)): sha(p) for p in
            (Path(__file__).resolve(), ROOT / "analysis/witness_refinement.py")}


def prepare(reference, bank_path, parents, root):
    measurement = verify_inputs(ROOT, reference)
    bank = read(bank_path)
    domain = bank["calibration"]["domain"]
    if domain not in ("mesh-temporal", "redmule-temporal") or measurement["measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]:
        raise ValueError("supported frozen measurement contract required")
    pool = []
    origins = {}
    for parent in sorted(parents):
        m = read(parent / "manifest.json")
        read(parent / "complete.json")
        origins[str(parent)] = sha(parent / "manifest.json")
        if m.get("kind", "").startswith("redmule-pulse-witness-"):
            if m["bank"] != bank or m["measurement"] != measurement:
                raise ValueError("pulse parent differs from requested bank")
            for case in m["cases"]:
                result = read(parent / "panel" / case["id"] / "result.json")["measurement"]
                if result["valid"]:
                    if result != read(parent / "cache" / result["cache_id"] / "result.json"):
                        raise ValueError("pulse parent differs from cache")
                    pool.append((case["split"], case["target"], case["program"], result["rates"], f"{parent.name}/{case['id']}"))
        else:
            if m["measurement_fingerprint"] != measurement["measurement_fingerprint"]:
                raise ValueError("parent measurement differs")
            matches = [split for split, part in bank["splits"].items()
                       if m["spec"]["targets"] == {r["id"]: r["rates"] for r in part["requests"]}]
            if len(matches) != 1:
                raise ValueError("parent target split ambiguous or different")
            for path in sorted((parent / "panel").glob("*/*/*/batches/*/trials.json")):
                target = path.relative_to(parent / "panel").parts[0]
                for trial in read(path):
                    if trial["valid"]:
                        cached = read(parent / "cache" / trial["cache_id"] / "result.json")
                        if cached["valid"] is not True or cached["rates"] != trial["rates"]:
                            raise ValueError("parent trial differs from cache")
                        pool.append((matches[0], target, trial["program"], trial["rates"], f"{parent.name}/{path.relative_to(parent)}/{trial['slot']}"))
    cases = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            candidates = [p for p in pool if p[:2] == (split, request["id"])]
            if not candidates:
                raise ValueError("every request requires a valid measured initial parent")
            best = min(candidates, key=lambda p: (error(p[3], request["rates"], bank["calibration"]["scale"]), p[4]))
            cases.append({"id": f"{split}-{request['id']}", "request": request,
                          "seed": 8000 if split == "development" else 8100,
                          "program": best[2], "rates": best[3], "origin": best[4]})
    root.mkdir(parents=True, exist_ok=False)
    write(root / "manifest.json", {"kind": "measured-witness-refinement-v4", "domain": domain,
                                   "measurement": measurement, "bank": bank, "parent_manifests": origins,
                                   "driver_sources": sources(), "cases": cases, "max_workers": 18})
    write(root / "freeze.json", {"manifest_sha256": sha(root / "manifest.json")})
    return {"cases": len(cases), "maximum_new_proposals": len(cases)*257}


def run(reference, root):
    if read(root / "freeze.json") != {"manifest_sha256": sha(root / "manifest.json")}:
        raise ValueError("frozen manifest changed")
    m = read(root / "manifest.json")
    if m["driver_sources"] != sources() or m["measurement"] != verify_inputs(ROOT, reference):
        raise ValueError("frozen measurement or refinement source changed")
    propose = runpy.run_path(ROOT / "analysis/witness_refinement.py")["pair"]
    scale = m["bank"]["calibration"]["scale"]
    design = backend(m["domain"])

    def cell(case):
        directory = root / "panel" / case["id"]
        best, _ = design.measured(case["program"], root, m["measurement"])
        if not best["valid"] or best["rates"] != case["rates"]:
            raise ValueError("initial parent failed exact replay")
        program = case["program"]
        ensure(directory / "initial.json", {"program": program, "measurement": best})
        slots = 1
        for batch in range(128):
            admission = qualify(case["request"], best, scale=scale, tolerance=.1, nonflat_margin=.02)
            if admission["qualified"]:
                break
            candidates = propose(program, batch, case["seed"])
            path = directory / f"batch-{batch:03}.json"
            rows = []
            for candidate in candidates:
                result, _ = design.measured(candidate, root, m["measurement"])
                rows.append({"program": candidate, "measurement": result})
            ensure(path, {"parent": program, "rows": rows})
            slots += 2
            for row in rows:
                result = row["measurement"]
                if result["valid"] and error(result["rates"], case["request"]["rates"], scale) < error(best["rates"], case["request"]["rates"], scale):
                    best, program = result, row["program"]
            print(json.dumps({"case": case["id"], "slots": slots,
                              "error": error(best["rates"], case["request"]["rates"], scale)}), flush=True)
        report = {"id": case["id"], "charged_slots": slots, "budget": 257,
                  "program": program, "measurement": best,
                  **qualify(case["request"], best, scale=scale, tolerance=.1, nonflat_margin=.02)}
        ensure(directory / "complete.json", report)
        return report

    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with concurrent.futures.ThreadPoolExecutor(max_workers=m["max_workers"]) as pool:
            reports = list(pool.map(cell, m["cases"]))
        summary = {"kind": m["kind"], "reports": reports}
        ensure(root / "complete.json", summary)
        return {"cases": len(reports), "qualified": sum(r["qualified"] for r in reports)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--parent", type=Path, action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        if args.bank is None or not args.parent:
            parser.error("prepare requires --bank and --parent")
        result = prepare(args.reference.resolve(), args.bank, [p.resolve() for p in args.parent], args.directory.resolve())
    else:
        if not args.execute:
            parser.error("run requires --execute")
        result = run(args.reference.resolve(), args.directory.resolve())
    print(json.dumps(result))


if __name__ == "__main__":
    main()
