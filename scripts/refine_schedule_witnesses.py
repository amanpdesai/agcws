"""Frozen CPU-only AES witness refinement with exact replay and immutable batches."""

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
    names = ("scripts/refine_schedule_witnesses.py", "analysis/schedule_refinement.py",
             "analysis/target_qualification.py", "docs/SCHEDULE_WITNESS_REFINEMENT.md")
    return {name: sha(ROOT / name) for name in names}


def prepare(reference, bank_path, parents, root):
    measurement = verify_inputs(ROOT, reference)
    bank = read(bank_path)
    domain = bank["calibration"]["domain"]
    if domain != "aes-temporal" or bank["calibration"]["measurement_fingerprint"] != measurement["measurement_fingerprint"]:
        raise ValueError("unchanged AES v2 measurement contract required")
    analyze = runpy.run_path(ROOT / "analysis/target_qualification.py")["analyze"]
    helpers = runpy.run_path(ROOT / "analysis/schedule_refinement.py")
    design = backend(domain)
    cases, origins = [], {}
    for split in ("development", "confirmation"):
        parent = parents[split]
        report = analyze(parent, bank_path, split)
        origins[split] = {"path": str(parent), "manifest_sha256": sha(parent / "manifest.json")}
        for request in bank["splits"][split]["requests"]:
            selected = next(r for r in report["requests"] if r["id"] == request["id"])["witness"]
            cases.append({"id": f"{split}-{request['id']}", "request": request,
                          "seed": 8300 if split == "development" else 8400,
                          "program": selected["program"], "rates": selected["rates"],
                          "origin": selected["cache_id"],
                          "initial_candidates": helpers["initial_schedules"](
                              request["rates"], bank["calibration"]["low"], design.contract, design.clock_edges)})
    root.mkdir(parents=True, exist_ok=False)
    write(root / "manifest.json", {"kind": "aes-schedule-witness-refinement-v3", "domain": domain,
                                   "measurement": measurement, "bank": bank, "parents": origins,
                                   "driver_sources": sources(), "cases": cases, "max_workers": 18,
                                   "budget": 260, "paired_batches": 128})
    write(root / "freeze.json", {"manifest_sha256": sha(root / "manifest.json")})
    return {"cases": len(cases), "maximum_slots": len(cases)*260}


def run(reference, root):
    if read(root / "freeze.json") != {"manifest_sha256": sha(root / "manifest.json")}:
        raise ValueError("frozen manifest changed")
    manifest = read(root / "manifest.json")
    if manifest["driver_sources"] != sources() or manifest["measurement"] != verify_inputs(ROOT, reference):
        raise ValueError("frozen runner or measurement changed")
    if manifest["budget"] != 260 or manifest["paired_batches"] != 128:
        raise ValueError("unexpected refinement budget")
    pair = runpy.run_path(ROOT / "analysis/schedule_refinement.py")["paired_transfer"]
    design = backend(manifest["domain"])
    scale = manifest["bank"]["calibration"]["scale"]

    def cell(case):
        directory = root / "panel" / case["id"]
        program = case["program"]
        best, _ = design.measured(program, root, manifest["measurement"])
        if not best["valid"] or best["rates"] != case["rates"]:
            raise ValueError("initial parent failed exact replay")
        ensure(directory / "initial.json", {"program": program, "measurement": best})
        slots = 1

        def admission():
            return qualify(case["request"], best, scale=scale, tolerance=.1, nonflat_margin=.02)

        def batch(path, candidates):
            nonlocal program, best, slots
            rows = [{"program": candidate, "measurement": design.measured(candidate, root, manifest["measurement"])[0]}
                    for candidate in candidates]
            ensure(path, {"parent": program, "rows": rows})
            slots += len(rows)
            for row in rows:
                result = row["measurement"]
                if result["valid"] and error(result["rates"], case["request"]["rates"], scale) < error(best["rates"], case["request"]["rates"], scale):
                    program, best = row["program"], result
            print(json.dumps({"case": case["id"], "slots": slots,
                              "error": error(best["rates"], case["request"]["rates"], scale)}), flush=True)

        if not admission()["qualified"]:
            batch(directory / "seeds.json", case["initial_candidates"])
        for index in range(128):
            if admission()["qualified"]:
                break
            batch(directory / f"batch-{index:03}.json", pair(program, design.contract, index, case["seed"]))
        result = {"id": case["id"], "charged_slots": slots, "budget": 260,
                  "program": program, "measurement": best, **admission()}
        ensure(directory / "complete.json", result)
        return result

    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with concurrent.futures.ThreadPoolExecutor(max_workers=manifest["max_workers"]) as pool:
            reports = list(pool.map(cell, manifest["cases"]))
        ensure(root / "complete.json", {"kind": manifest["kind"], "reports": reports})
    return {"cases": len(reports), "qualified": sum(r["qualified"] for r in reports)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--development", type=Path)
    parser.add_argument("--confirmation", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        if not all((args.bank, args.development, args.confirmation)):
            parser.error("prepare requires bank and both parent splits")
        result = prepare(args.reference.resolve(), args.bank.resolve(),
                         {s: getattr(args, s).resolve() for s in ("development", "confirmation")},
                         args.directory.resolve())
    else:
        if not args.execute:
            parser.error("run requires --execute")
        result = run(args.reference.resolve(), args.directory.resolve())
    print(json.dumps(result))
