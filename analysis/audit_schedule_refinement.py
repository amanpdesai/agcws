"""Reconstruct AES seed/paired refinement from compact evidence, without simulation."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import source_inventory
from agcws.pipeline.metrics import error, key
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def analyze(root):
    manifest = read(root / "manifest.json")
    digest = hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()
    if read(root / "freeze.json") != {"manifest_sha256": digest}:
        raise ValueError("manifest checksum differs")
    if (manifest["kind"] != "aes-schedule-witness-refinement-v3" or manifest["domain"] != "aes-temporal"
            or manifest["budget"] != 260 or manifest["paired_batches"] != 128):
        raise ValueError("unknown refinement contract")
    if source_inventory(ROOT, manifest["domain"]) != manifest["measurement"]["sources"]:
        raise ValueError("measurement sources differ")
    expected_sources = runpy.run_path(ROOT / "scripts/refine_schedule_witnesses.py")["sources"]()
    if manifest["driver_sources"] != expected_sources:
        raise ValueError("refinement source inventory differs")
    for name, expected in manifest["driver_sources"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError("frozen refinement source differs")
    helper = runpy.run_path(ROOT / "analysis/schedule_refinement.py")
    design, bank = backend(manifest["domain"]), manifest["bank"]
    scale = bank["calibration"]["scale"]
    expected_cases = {f"{split}-{r['id']}": (split, r) for split, part in bank["splits"].items()
                      for r in part["requests"]}
    if (len(expected_cases) != 18 or len(manifest["cases"]) != 18
            or {case["id"] for case in manifest["cases"]} != set(expected_cases)):
        raise ValueError("missing, duplicate or unexpected request cases")
    checked = set()

    def measurement(program, result):
        identifier = result.get("cache_id")
        if not result["valid"]:
            if result.get("rates") is not None or result.get("profile") is not None:
                raise ValueError("invalid proposal was scored")
            if not identifier:
                checks = (design.adapter().validate_schema, design.adapter().validate_protocol)
                rejected = next((v for check in checks if not (v := check(program)).valid), None)
                if rejected is None or rejected.stage.value != result["stage"]:
                    raise ValueError("unmeasured rejection disagrees with native validation")
                return
        canonical = design.canonical(program)
        if identifier != key({"program": canonical, "measurement": manifest["measurement"]["measurement_fingerprint"]}):
            raise ValueError("cache identity differs")
        cache = root / "cache" / identifier
        if read(cache / "result.json") != result:
            raise ValueError("cache result differs")
        if not result["valid"] or identifier in checked:
            return
        matches = list(cache.glob("attempt-*/activity.json"))
        if len(matches) != 1:
            raise ValueError("missing or ambiguous activity evidence")
        attempt = matches[0].parent
        if read(attempt / "program.json") != canonical or not design.completed(attempt)["valid"]:
            raise ValueError("executed workload or completion differs")
        activity = read(matches[0])
        edges, samples = design.clock_edges, activity["per_cycle_toggles"]
        if activity["clock_edges"] != edges or len(samples) != edges:
            raise ValueError("activity window differs")
        rates = [sum(samples[i*edges//8:(i+1)*edges//8])/((i+1)*edges//8-i*edges//8) for i in range(8)]
        profile = result["profile"]
        if (rates != result["rates"] or rates != profile["window_rates"]
                or profile["scope"] != design.scope or profile["fidelity"] != "activity"
                or profile["useful_work"] != 64):
            raise ValueError("measured profile does not reconstruct")
        checked.add(identifier)

    reports = []
    for case in manifest["cases"]:
        split, request = expected_cases[case["id"]]
        expected_seed = 8300 if split == "development" else 8400
        seeds = helper["initial_schedules"](request["rates"], bank["calibration"]["low"], design.contract, design.clock_edges)
        if case["request"] != request or case["seed"] != expected_seed or case["initial_candidates"] != seeds:
            raise ValueError("case differs from declared request/initialization")
        directory = root / "panel" / case["id"]
        initial = read(directory / "initial.json")
        program, best = initial["program"], initial["measurement"]
        if program != case["program"] or best["rates"] != case["rates"] or not best["valid"]:
            raise ValueError("initial exact replay differs")
        measurement(program, best)
        slots = 1

        def admission():
            return qualify(request, best, scale=scale, tolerance=.1, nonflat_margin=.02)

        def consume(path, candidates):
            nonlocal program, best, slots
            if admission()["qualified"]:
                raise ValueError("proposals emitted after qualification")
            batch = read(path)
            if batch["parent"] != program or [r["program"] for r in batch["rows"]] != candidates:
                raise ValueError("batch differs from frozen proposals or parent")
            slots += len(candidates)
            for row in batch["rows"]:
                result = row["measurement"]
                measurement(row["program"], result)
                if result["valid"] and error(result["rates"], request["rates"], scale) < error(best["rates"], request["rates"], scale):
                    program, best = row["program"], result

        seed_path = directory / "seeds.json"
        if seed_path.exists():
            consume(seed_path, seeds)
        elif not admission()["qualified"]:
            raise ValueError("missing seed batch")
        batches = sorted(directory.glob("batch-*.json"))
        if len(batches) > 128:
            raise ValueError("paired budget exceeded")
        for index, path in enumerate(batches):
            if path.name != f"batch-{index:03}.json":
                raise ValueError("noncontiguous paired batches")
            consume(path, helper["paired_transfer"](program, design.contract, index, case["seed"]))
        report = {"id": case["id"], "charged_slots": slots, "budget": 260,
                  "program": program, "measurement": best, **admission()}
        if not report["qualified"] and slots != 260:
            raise ValueError("unsolved request stopped before budget exhaustion")
        if report != read(directory / "complete.json"):
            raise ValueError("request terminal result differs")
        reports.append(report)
    if read(root / "complete.json") != {"kind": manifest["kind"], "reports": reports}:
        raise ValueError("panel summary differs")
    return {"scope": "decisions, functional records and activity arithmetic; no independent waveform resimulation",
            "cases": len(reports), "qualified": sum(r["qualified"] for r in reports),
            "charged_slots": sum(r["charged_slots"] for r in reports),
            "unique_profiles_checked": len(checked), "manifest_sha256": digest}


def admitted_bank(root):
    audit = analyze(root)
    if audit["cases"] != 18 or audit["qualified"] != 18:
        raise ValueError("all eight non-flat targets and both controls must qualify")
    manifest = read(root / "manifest.json")
    reports = {r["id"]: r for r in read(root / "complete.json")["reports"]}
    splits = {}
    for split, part in manifest["bank"]["splits"].items():
        if len(part["requests"]) != 9 or sum(r["control"] for r in part["requests"]) != 1:
            raise ValueError("eight targets plus separate control required per split")
        requests = []
        for request in part["requests"]:
            report = reports[f"{split}-{request['id']}"]
            requests.append({**request, "qualified": True, "witness_error": report["witness_error"],
                             "witness_cache_id": report["measurement"]["cache_id"], "witness_case": report["id"]})
        splits[split] = {"requests": requests, "pairwise_distances": part["pairwise_distances"]}
    return {"scope": "qualified activity targets, not full-study readiness or gate-power evidence",
            "domain": manifest["domain"], "target_bank_qualified": True, "full_study_ready": False,
            "audit": audit, "calibration": manifest["bank"]["calibration"],
            "qualification_procedures": [manifest["bank"]["procedure"], "docs/SCHEDULE_WITNESS_REFINEMENT.md"],
            "splits": splits}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--admit-bank", action="store_true")
    args = parser.parse_args()
    write(args.output, (admitted_bank if args.admit_bank else analyze)(args.directory))
