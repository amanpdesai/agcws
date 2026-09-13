"""Reconstruct local refinement decisions and window arithmetic without simulation."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import source_inventory
from agcws.pipeline.metrics import error
from agcws.pipeline.metrics import key as cache_key
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def analyze(root):
    m = read(root / "manifest.json")
    if read(root / "freeze.json")["manifest_sha256"] != hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest():
        raise ValueError("manifest checksum differs")
    if source_inventory(ROOT, m["domain"]) != m["measurement"]["sources"]:
        raise ValueError("audit measurement source differs")
    for name, expected in m["driver_sources"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError("refinement source differs")
    propose = runpy.run_path(ROOT / "analysis/witness_refinement.py")["pair"]
    design = backend(m["domain"])
    scale = m["bank"]["calibration"]["scale"]
    checked = set()

    def measurement(program, result):
        key = result.get("cache_id")
        if key and key != cache_key({"program": design.canonical(program),
                                    "measurement": m["measurement"]["measurement_fingerprint"]}):
            raise ValueError("cache identity differs from proposed workload")
        if key and read(root / "cache" / key / "result.json") != result:
            raise ValueError("measurement differs from cached record")
        if not result["valid"]:
            if "rates" in result or "profile" in result:
                raise ValueError("invalid proposal was scored")
            return
        if key in checked:
            return
        cache = root / "cache" / key
        attempts = list(cache.glob("attempt-*/activity.json"))
        if len(attempts) != 1:
            raise ValueError("missing or ambiguous waveform activity")
        attempt = attempts[0].parent
        if read(attempt / "program.json") != design.canonical(program):
            raise ValueError("executed workload differs")
        if not design.completed(attempt)["valid"]:
            raise ValueError("functional records do not pass")
        activity = read(attempt / "activity.json")
        samples = activity["per_cycle_toggles"]
        edges = design.clock_edges
        if activity["clock_edges"] != edges or len(samples) != edges:
            raise ValueError("observation window differs")
        rates = [sum(samples[i*edges//8:(i+1)*edges//8])/((i+1)*edges//8-i*edges//8) for i in range(8)]
        if (rates != result["rates"] or rates != result["profile"]["window_rates"]
                or result["profile"]["scope"] != design.scope or result["profile"]["fidelity"] != "activity"):
            raise ValueError("profile does not reconstruct from activity")
        checked.add(key)

    reports = []
    for case in m["cases"]:
        directory = root / "panel" / case["id"]
        initial = read(directory / "initial.json")
        program, best = initial["program"], initial["measurement"]
        if program != case["program"] or best["rates"] != case["rates"]:
            raise ValueError("initial replay differs")
        measurement(program, best)
        batches = sorted(directory.glob("batch-*.json"))
        if len(batches) > 128:
            raise ValueError("refinement budget exceeded")
        for index, path in enumerate(batches):
            if path.name != f"batch-{index:03}.json":
                raise ValueError("noncontiguous batches")
            if qualify(case["request"], best, scale=scale, tolerance=.1, nonflat_margin=.02)["qualified"]:
                raise ValueError("proposals emitted after qualification")
            batch = read(path)
            proposals = propose(program, index, case["seed"])
            if batch["parent"] != program or [r["program"] for r in batch["rows"]] != proposals:
                raise ValueError("paired proposals do not match frozen decision rule")
            for row in batch["rows"]:
                measurement(row["program"], row["measurement"])
                result = row["measurement"]
                if result["valid"] and error(result["rates"], case["request"]["rates"], scale) < error(best["rates"], case["request"]["rates"], scale):
                    best, program = result, row["program"]
        report = {"id": case["id"], "charged_slots": 1+2*len(batches), "budget": 257,
                  "program": program, "measurement": best,
                  **qualify(case["request"], best, scale=scale, tolerance=.1, nonflat_margin=.02)}
        if not report["qualified"] and len(batches) != 128:
            raise ValueError("unsolved run stopped before budget")
        if report != read(directory / "complete.json"):
            raise ValueError("terminal report differs from reconstruction")
        reports.append(report)
    if read(root / "complete.json") != {"kind": m["kind"], "reports": reports}:
        raise ValueError("panel summary differs")
    return {"scope": "decision, functional-record and activity arithmetic audit; no independent waveform resimulation",
            "domain": m["domain"], "cases": len(reports), "qualified": sum(r["qualified"] for r in reports),
            "charged_slots": sum(r["charged_slots"] for r in reports), "unique_profiles_checked": len(checked),
            "manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()}


def admitted_bank(root):
    audit = analyze(root)
    if audit["cases"] != 18 or audit["qualified"] != 18:
        raise ValueError("both nine-request splits must qualify before bank admission")
    manifest = read(root / "manifest.json")
    reports = {r["id"]: r for r in read(root / "complete.json")["reports"]}
    splits = {}
    for split, source in manifest["bank"]["splits"].items():
        if len(source["requests"]) != 9 or sum(r["control"] for r in source["requests"]) != 1:
            raise ValueError("eight non-flat requests and one control required")
        requests = []
        for request in source["requests"]:
            report = reports[f"{split}-{request['id']}"]
            requests.append({**request, "qualified": True,
                             "witness_error": report["witness_error"],
                             "witness_cache_id": report["measurement"]["cache_id"],
                             "witness_case": report["id"]})
        splits[split] = {"requests": requests, "pairwise_distances": source["pairwise_distances"]}
    return {"scope": "qualified activity targets; not full-study readiness or gate-power evidence",
            "domain": manifest["domain"], "target_bank_qualified": True, "full_study_ready": False,
            "calibration": manifest["bank"]["calibration"], "audit": audit,
            "qualification_procedures": [manifest["bank"]["procedure"], "docs/WITNESS_REFINEMENT_V4.md"],
            "splits": splits}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--admit-bank", action="store_true")
    args = parser.parse_args()
    write(args.output, (admitted_bank if args.admit_bank else analyze)(args.directory))
