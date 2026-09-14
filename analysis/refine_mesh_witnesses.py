"""Frozen CPU-only local witness refinement; never a comparative policy arm."""

import argparse
import concurrent.futures
import copy
import random
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import distance, qualify
from agcws.provenance import file_sha256


def prepare(source, destination):
    manifest = verify_inputs(ROOT, source / "reference")
    bank = read(source / "qualification/requested-bank.json")
    admission = read(source / "qualification/admission.json")
    attempts = read(source / "qualification/audited-attempts.json")
    cases = []
    for outcome in sorted(admission["outcomes"], key=lambda r: r["id"]):
        if outcome["qualified"]:
            continue
        target = next(t for s, p in bank["splits"].items() for t in p["requests"]
                      if s+"-"+t["id"] == outcome["id"])
        best = min((r for r in attempts if r["id"] == outcome["id"] and r["valid"]),
                   key=lambda r: (r["witness_error"], r["source"], r.get("slot", 0)))
        cases.append({"id": outcome["id"], "target": target, "initial": best,
                      "seed": 7500+len(cases)})
    if len(cases) != 4:
        raise ValueError("exactly four declared misses required")
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "manifest.json", {
        "reference": str(source / "reference"), "measurement": manifest,
        "source_admission_sha256": file_sha256(source / "qualification/admission.json"),
        "driver_sha256": file_sha256(Path(__file__)),
        "procedure_sha256": file_sha256(ROOT / "docs/MESH_BIT_REFINEMENT_V1.md"),
        "scale": bank["calibration"]["scale"], "budget": 512, "cases": cases})


def mutate(program, rng):
    child = copy.deepcopy(program)
    phase = rng.choice(child["phases"])
    field = rng.choice(["start", "duration", "packets"])
    delta = rng.choice([-1, 1])*rng.choice([1, 4, 16, 64])
    bounds = {"start": (0, 8191), "duration": (1, 8192), "packets": (1, 512)}
    low, high = bounds[field]
    phase[field] = min(high, max(low, phase[field]+delta))
    return child


def run(root):
    manifest = read(root / "manifest.json")
    if (manifest["measurement"] != verify_inputs(ROOT, Path(manifest["reference"]))
            or manifest["driver_sha256"] != file_sha256(Path(__file__))
            or manifest["procedure_sha256"] != file_sha256(ROOT / "docs/MESH_BIT_REFINEMENT_V1.md")):
        raise ValueError("frozen refinement changed")
    design = backend("mesh-temporal")

    def cell(case):
        rng = random.Random(case["seed"])
        parent = case["initial"]["program"]
        best_error = case["initial"]["witness_error"]
        best_rates = case["initial"]["rates"]
        for slot in range(1, manifest["budget"]+1):
            program = mutate(parent, rng)
            path = root / "panel" / case["id"] / f"{slot:04}.json"
            if path.exists():
                row = read(path)
                if row["program"] != program or row["parent"] != parent:
                    raise ValueError("resume trajectory differs")
                result = row["measurement"]
            else:
                result, _ = design.measured(program, root, manifest["measurement"])
            error = distance(result["profile"]["window_rates"], case["target"]["rates"], manifest["scale"]) if result["valid"] else None
            row = {"slot": slot, "program": program, "parent": parent,
                   "measurement": result, "error": error}
            ensure(path, row)
            if error is not None and error < best_error:
                parent, best_error, best_rates = program, error, result["profile"]["window_rates"]
        outcome = qualify(case["target"], {"valid": True, "rates": best_rates},
                          scale=manifest["scale"], tolerance=.1, nonflat_margin=.02)
        return {"id": case["id"], "program": parent, "rates": best_rates,
                "initial_error": case["initial"]["witness_error"], "charged_slots": 512, **outcome}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(cell, manifest["cases"]))
    ensure(root / "complete.json", {"outcomes": outcomes, "charged_slots": 2048,
                                     "qualified": sum(r["qualified"] for r in outcomes)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.source.resolve(), args.root.resolve())
    else:
        run(args.root.resolve())
