"""Exact replay bridge: old calibration and admitted witnesses, never new targets."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.calibration import report
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.storage import read, write


def comparable(row):
    return {k: row.get(k) for k in ("valid", "stage", "rates", "profile")}


def plan(calibration, witnesses, bank_path, destination):
    bank = read(bank_path)
    if report(calibration) != bank["calibration"]:
        raise ValueError("calibration does not reproduce admitted bank")
    rows = [t for p in sorted((calibration / "panel").rglob("trials.json")) for t in read(p)]
    cases = [{"id": f"calibration-{i:02}", "program": t["program"]} for i, t in enumerate(rows)]
    expected = {c["id"]: comparable(t) for c, t in zip(cases, rows, strict=True)}
    reports = {r["id"]: r for r in read(witnesses / "complete.json")["reports"]}
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            name = f"{split}-{request['id']}"
            row = reports[name]
            if not row["qualified"] or row["measurement"]["cache_id"] != request["witness_cache_id"]:
                raise ValueError("witness identity differs")
            cases.append({"id": name, "program": row["program"]})
            expected[name] = comparable(row["measurement"])
    if len(cases) != 82:
        raise ValueError("64 calibration plus 18 witness cases required")
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "expected.json", expected)
    write(destination / "old-bank.json", bank)
    write(destination / "lineage.json", {"bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
          "calibration_manifest_sha256": hashlib.sha256((calibration / "manifest.json").read_bytes()).hexdigest(),
          "witness_manifest_sha256": hashlib.sha256((witnesses / "manifest.json").read_bytes()).hexdigest()})
    config = {"name": f"{bank['domain']}-runtime-replay-v2", "domain": bank["domain"],
              "scope": "exact calibration and witness replay; not a new policy comparison",
              "max_workers": 18, "cases": cases}
    write(destination / "config.json", config)
    spec = read(calibration / "manifest.json")["spec"]
    write(destination / "reference-spec.json", spec)
    prepare(ROOT, destination / "reference-spec.json", destination / "reference")
    runner = runpy.run_path(ROOT / "scripts/probe_fixed_cases.py")
    runner["prepare"](destination / "reference", destination / "config.json", destination / "replay")
    write(destination / "freeze.json", {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
          for p in destination.glob("*.json")})
    return {"cases": len(cases), "executed": False}


def audit(root):
    for name, digest in read(root / "freeze.json").items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError("frozen replay inputs changed")
    manifest = read(root / "replay/manifest.json")
    if manifest["measurement"] != verify_inputs(ROOT, root / "reference"):
        raise ValueError("measurement reference differs")
    if manifest["config"] != read(root / "config.json"):
        raise ValueError("replay configuration differs")
    if manifest["driver_sha256"] != hashlib.sha256((ROOT / "scripts/probe_fixed_cases.py").read_bytes()).hexdigest():
        raise ValueError("replay driver differs")
    if hashlib.sha256((root / "replay/manifest.json").read_bytes()).hexdigest() != read(root / "replay/freeze.json")["manifest_sha256"]:
        raise ValueError("replay manifest changed")
    expected = read(root / "expected.json")
    complete = read(root / "replay/complete.json")
    if complete["charged_slots"] != 82 or len(complete["results"]) != 82:
        raise ValueError("complete replay required")
    for case, row in zip(manifest["config"]["cases"], complete["results"], strict=True):
        if row["id"] != case["id"] or row["program"] != case["program"]:
            raise ValueError("replayed input differs")
        if comparable(row["measurement"]) != expected[row["id"]]:
            raise ValueError(f"measurement changed: {row['id']}")
        if read(root / "replay/panel" / row["id"] / "result.json") != row:
            raise ValueError("replay checkpoint differs")
        result = row["measurement"]
        if read(root / "replay/cache" / result["cache_id"] / "result.json") != result:
            raise ValueError("replay cache differs")
    return {"cases": 82, "exact_measurement_match": True, "full_study_ready": False,
            "old_measurement_fingerprint": read(root / "old-bank.json")["calibration"]["measurement_fingerprint"],
            "new_measurement_fingerprint": manifest["measurement"]["measurement_fingerprint"],
            "scope": "exact rates, validity and complete profile replay, not a policy comparison"}


def admitted_bank(root):
    checked = audit(root)
    bank = read(root / "old-bank.json")
    bank["calibration"] = {**bank["calibration"], "measurement_fingerprint": checked["new_measurement_fingerprint"]}
    measured = {r["id"]: r["measurement"] for r in read(root / "replay/complete.json")["results"]}
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            request["witness_cache_id"] = measured[f"{split}-{request['id']}"]["cache_id"]
            request["witness_case"] = f"{split}-{request['id']}"
    bank["runtime_replay"] = {**checked, "lineage": read(root / "lineage.json")}
    bank["qualification_procedures"].append("docs/RUNTIME_REPLAY_V2.md")
    bank["full_study_ready"] = False
    return bank


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "audit", "admit"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--witnesses", type=Path)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "plan":
        if None in (args.calibration, args.witnesses, args.bank):
            parser.error("plan requires calibration, witnesses and bank")
        print(plan(args.calibration, args.witnesses, args.bank, args.directory))
    elif args.action == "admit":
        if args.output is None:
            parser.error("admit requires output")
        write(args.output, admitted_bank(args.directory))
    else:
        write(args.directory / "audit.json", audit(args.directory))
