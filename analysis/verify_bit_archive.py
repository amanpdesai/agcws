"""Recompute archived calibration, target construction, qualification and cross-solves offline."""

import argparse
import gzip
import hashlib
import json
import runpy
from pathlib import Path

from bit_bank import calibration

from agcws.config import ROOT
from agcws.pipeline.targets import distance, qualify, requests


def verify(directory):
    with gzip.open(directory / "inputs.json.gz", "rt") as stream:
        bundle = json.load(stream)
    for record in bundle.values():
        if hashlib.sha256(record["text"].encode()).hexdigest() != record["sha256"]:
            raise ValueError("input bundle digest differs")

    def read(name):
        return json.loads(bundle[name]["text"])

    freeze = read("qualification/target-freeze.json")
    for key, name in (("requested_bank_sha256", "qualification/requested-bank.json"),
                      ("calibration_sha256", "qualification/calibration.json"),
                      ("replay_complete_sha256", "replay/complete.json")):
        if freeze[key] != bundle[name]["sha256"]:
            raise ValueError("target-freeze digest differs")
    bank = read("qualification/requested-bank.json")
    cal = calibration(read("replay/complete.json")["results"])
    if cal != bank["calibration"] or cal != read("qualification/calibration.json"):
        raise ValueError("calibration differs")
    fixed = runpy.run_path(ROOT / "scripts/prepare_target_bank.py")["fixed_work_requests"]
    attempts = read("qualification/audited-attempts.json")
    admission = read("qualification/admission.json")
    targets = {}
    for split, part in bank["splits"].items():
        expected = (fixed(cal["low"], cal["high"], cal["median_window_mean"], split)
                    if bank["domain"] in ("aes-temporal", "dma-temporal")
                    else requests(cal["low"], cal["high"], split=split))
        if expected != part["requests"]:
            raise ValueError("requested vectors differ from declared construction")
        for target in expected:
            targets[f"{split}-{target['id']}"] = target
    for outcome in admission["outcomes"]:
        target = targets[outcome["id"]]
        rows = [r for r in attempts if r["id"] == outcome["id"]]
        original = [r for r in rows if r["source"] == "fixed-original-witness"]
        if len(original) != 1:
            raise ValueError("one original witness attempt required")
        needed = not original[0]["qualified"] and (target["control"] or target["constant_floor"] > .12)
        if len(rows) != (513 if needed else 1):
            raise ValueError("declared witness budget differs")
        for arm in ("phase-random", "phase-ga"):
            slots = [r["slot"] for r in rows if r["source"] == arm]
            if slots != (list(range(1, 257)) if needed else []):
                raise ValueError("classical proposal axis differs")
        for row in rows:
            result = qualify(target, row, scale=cal["scale"], tolerance=.1, nonflat_margin=.02)
            if any(row[k] != v for k, v in result.items()):
                raise ValueError("qualification arithmetic differs")
        successful = [r for r in rows if r["qualified"]]
        best = min(successful, key=lambda r: (r["witness_error"], r["source"], r.get("slot", 0))) if successful else None
        if (outcome["witness"] != best or outcome["qualified"] != bool(successful)
                or outcome["attempts"] != len(rows)):
            raise ValueError("admitted witness differs")
    if (admission["charged_witness_attempts"] != len(attempts)
            or admission["qualified"] != sum(r["qualified"] for r in admission["outcomes"])):
        raise ValueError("admission accounting differs")
    witnesses = {r["id"]: r["witness"] for r in admission["outcomes"]}
    for row in read("qualification/cross-solves.json"):
        error = distance(witnesses[row["witness"]]["rates"], targets[row["target"]]["rates"], cal["scale"])
        if error != row["error"] or row["within_tolerance"] != (error <= .1):
            raise ValueError("cross-solve arithmetic differs")
    published = json.loads((directory / "bank.json").read_text())
    if published != {**bank, "admission": admission, "task_bank_qualified": admission["task_bank_qualified"]}:
        raise ValueError("published bank differs")
    return {"domain": bank["domain"], "verified": True, "qualified": admission["qualified"],
            "attempts": len(attempts), "scope": "offline arithmetic, not waveform resimulation"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory)))
