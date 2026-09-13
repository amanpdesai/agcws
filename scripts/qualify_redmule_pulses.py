"""Versioned witness search using pulse proposals and the real shared evaluator."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import error
from agcws.pipeline.redmule import RedmuleTemporal
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import qualify


def sources():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), ROOT / "analysis/pulse_candidates.py")}


def prepare(reference, probe, bank_path, root):
    measurement = verify_inputs(ROOT, reference)
    bank = read(bank_path)
    if (measurement != read(probe / "manifest.json")["measurement"]
            or measurement["measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]
            or read(probe / "complete.json")["cases"] != 54):
        raise ValueError("pulse, calibration and measurement contracts differ")
    pulses = {}
    for pattern in ("zeros", "alternating", "random"):
        case = read(probe / "panel" / f"size16-{pattern}-x1-queued" / "result.json")
        attempt = probe / "cache" / case["measurement"]["cache_id"] / "attempt-001"
        functional = read(attempt / "functional.json")
        if functional["valid"] is not True or functional["completed_jobs"] != 1:
            raise ValueError("valid single-job pulse required")
        pulses[pattern] = {"samples": read(attempt / "activity.json")["per_cycle_toggles"],
                           "completion": functional["job_completions"][0][1]}
    propose = runpy.run_path(ROOT / "analysis/pulse_candidates.py")["propose"]
    cases, attempts = [], []
    for split, seed in (("development", 7600), ("confirmation", 7700)):
        for request in bank["splits"][split]["requests"]:
            for pattern, pulse in pulses.items():
                candidates = propose(request["rates"], pulse["samples"], pulse["completion"], pattern=pattern, seed=seed)
                counts = {len(c["program"]["phases"]) for c in candidates}
                attempts.append({"split": split, "target": request["id"], "pattern": pattern,
                                 "unplaced_job_counts": sorted(set(range(1, 9))-counts)})
                for candidate in candidates:
                    cases.append({"id": f"{split}-{request['id']}-{pattern}-{len(candidate['program']['phases'])}",
                                  "split": split, "target": request["id"], **candidate})
    root.mkdir(parents=True, exist_ok=False)
    write(root / "manifest.json", {"kind": "redmule-pulse-witness-v2", "measurement": measurement,
                                   "driver_sources": sources(), "bank": bank, "cases": cases,
                                   "proposal_attempts": attempts, "max_workers": 18})
    write(root / "pulse_inputs.json", pulses)
    write(root / "freeze.json", {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                 for name in ("manifest.json", "pulse_inputs.json")})
    return {"prepared_cases": len(cases)}


def run(reference, root):
    if read(root / "freeze.json") != {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                      for name in ("manifest.json", "pulse_inputs.json")}:
        raise ValueError("frozen witness files changed")
    manifest = read(root / "manifest.json")
    if manifest["driver_sources"] != sources() or manifest["measurement"] != verify_inputs(ROOT, reference):
        raise ValueError("frozen witness inputs changed")
    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

        def measure(case):
            result, _ = RedmuleTemporal().measured(case["program"], root, manifest["measurement"])
            record = {"id": case["id"], "measurement": result}
            ensure(root / "panel" / case["id"] / "result.json", record)
            print(json.dumps({"case": case["id"], "valid": result["valid"]}), flush=True)
            return result

        with concurrent.futures.ThreadPoolExecutor(max_workers=manifest["max_workers"]) as pool:
            results = list(pool.map(measure, manifest["cases"]))
        reports = []
        scale = manifest["bank"]["calibration"]["scale"]
        for split in ("development", "confirmation"):
            for request in manifest["bank"]["splits"][split]["requests"]:
                valid = [(error(result["rates"], request["rates"], scale), case["id"], result)
                         for case, result in zip(manifest["cases"], results, strict=True)
                         if case["split"] == split and case["target"] == request["id"] and result["valid"]]
                selected = min(valid, key=lambda row: row[:2]) if valid else None
                reports.append({"split": split, "target": request["id"],
                                "witness_case": selected[1] if selected else None,
                                **qualify(request, selected[2] if selected else {"valid": False},
                                          scale=scale, tolerance=0.1, nonflat_margin=0.02)})
        summary = {"kind": manifest["kind"], "cases": len(results), "reports": reports}
        ensure(root / "complete.json", summary)
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--probe", type=Path)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        if args.probe is None or args.bank is None:
            parser.error("prepare requires --probe and --bank")
        result = prepare(args.reference.resolve(), args.probe.resolve(), args.bank, args.directory.resolve())
    else:
        if not args.execute:
            parser.error("run requires --execute")
        result = run(args.reference.resolve(), args.directory.resolve())
    print(json.dumps(result))


if __name__ == "__main__":
    main()
