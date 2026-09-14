"""Audit every frozen bin-constructor attempt before selecting measured witnesses."""

import argparse
import copy
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import error
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def audit(root, bank):
    manifest, complete = read(root / "manifest.json"), read(root / "complete.json")
    if manifest["measurement"]["measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]:
        raise ValueError("bank and evaluator fingerprints differ")
    expected = manifest["config"]["cases"]
    rows = complete["results"]
    if complete["charged_slots"] != 486 or len(rows) != 486 or len(expected) != 486:
        raise ValueError("complete frozen 486-slot panel required")
    for case, row in zip(expected, rows, strict=True):
        if case != {key: row[key] for key in ("id", "program")}:
            raise ValueError("frozen candidate order or content changed")
        stored = read(root / "panel" / row["id"] / "result.json")
        if stored != row:
            raise ValueError("completion differs from per-case record")
        result = row["measurement"]
        if result["valid"]:
            cache = root / "cache" / result["cache_id"]
            cached = read(cache / "result.json")
            if cached["canonical_program"] != case["program"] or any(
                    cached[k] != result[k] for k in ("valid", "rates", "profile", "cache_id")):
                raise ValueError("native cached program or measurement differs")
            attempts = list(cache.glob("attempt-*/activity.json"))
            if len(attempts) != 1:
                raise ValueError("exactly one measured trace required")
            activity = read(attempts[0])
            functional = read(attempts[0].with_name("functional.json"))
            jobs = sum(p["jobs"] for p in case["program"]["phases"])
            if (activity["clock_edges"] != 262144
                    or [v/32768 for v in activity["window_toggles"]] != result["rates"]
                    or not functional["valid"] or functional["completed_jobs"] != jobs
                    or functional["useful_work"] != jobs*case["program"]["size"]**3
                    or functional["useful_work"] < 1024):
                raise ValueError("functional work or integer activity arithmetic differs")
    reports = []
    scale = bank["calibration"]["scale"]
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            subset = [r for r in rows if r["id"].split("--")[:2] == [split, request["id"]]]
            if len(subset) != 27:
                raise ValueError("27 attempts per request required")
            valid = [r for r in subset if r["measurement"]["valid"]]
            selected = min(valid, key=lambda r: (error(r["measurement"]["rates"], request["rates"], scale), r["id"])) if valid else None
            reports.append({"split": split, "target": request["id"], "attempts": 27,
                            "valid": len(valid), "witness_case": selected["id"] if selected else None,
                            **qualify(request, selected["measurement"] if selected else {"valid": False},
                                      scale=scale, tolerance=.1, nonflat_margin=.02)})
    return {"charged_slots": 486, "qualified": sum(r["qualified"] for r in reports),
            "reports": reports, "full_study_ready": False,
            "manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
            "scope": "expert constructor feasibility only; not policy comparison"}


def admit(root, bank, reference):
    manifest = read(root / "manifest.json")
    if verify_inputs(ROOT, reference) != manifest["measurement"]:
        raise ValueError("current runtime differs from measured witness runtime")
    checked = audit(root, bank)
    if checked["qualified"] != 18:
        raise ValueError("all eighteen requests must qualify")
    result = copy.deepcopy(bank)
    measured = {r["id"]: r["measurement"] for r in read(root / "complete.json")["results"]}
    reports = {(r["split"], r["target"]): r for r in checked["reports"]}
    for split, part in result["splits"].items():
        for request in part["requests"]:
            record = reports[split, request["id"]]
            request.update(qualified=True, witness_error=record["witness_error"],
                           witness_case=record["witness_case"],
                           witness_cache_id=measured[record["witness_case"]]["cache_id"])
    result.update(domain=manifest["measurement"]["spec"]["domain"],
                  target_bank_qualified=True, full_study_ready=False, audit=checked,
                  qualification_procedures=["docs/REDMULE_LONG_WINDOW_V1.md", "docs/REDMULE_BIN_WITNESS_V1.md"],
                  scope="qualified activity targets; witnesses excluded from policy payloads")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--admit", action="store_true")
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    if args.admit and args.reference is None:
        parser.error("admission requires current-runtime reference")
    write(args.output, admit(args.directory, read(args.bank), args.reference) if args.admit
          else audit(args.directory, read(args.bank)))
