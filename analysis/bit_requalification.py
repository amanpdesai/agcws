"""Freeze existing programs for new-metric native CPU remeasurement."""

import argparse
import gzip
import hashlib
import json
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare
from agcws.pipeline.storage import read, write

DESIGNS = ("aes", "dma", "mesh", "ibex", "redmule")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixed_cases(bundle, design):
    witness_key = ("out/ibex-bank-admission-v5/run/complete.json" if design == "ibex"
                   else f"out/{design}-runtime-replay-v5/replay/complete.json")
    calibration_key = "out/ibex-calibration-replay-v5/run/complete.json" if design == "ibex" else witness_key
    calibration = bundle[calibration_key]["data"]["results"]
    witnesses = bundle[witness_key]["data"]["results"]
    cases = [{"id": row["id"], "program": row["program"]} for row in calibration
             if row["id"].startswith("calibration-")]
    cases += [{"id": row["id"], "program": row["program"]} for row in witnesses
              if row["id"].startswith(("development-", "confirmation-"))]
    if len(cases) != 82 or len({c["id"] for c in cases}) != 82:
        raise ValueError("exact 64 calibration and 18 witness programs required")
    return sorted(cases, key=lambda c: c["id"])


def plan(destination, design):
    archive = ROOT / "results/task_quality_v1/inputs.json.gz"
    with gzip.open(archive, "rt") as stream:
        bundle = json.load(stream)
    for record in bundle.values():
        if hashlib.sha256(json.dumps(record["data"], sort_keys=True).encode()).hexdigest() != record["canonical_sha256"]:
            raise ValueError("audit input content changed")
    bank_path = ROOT / f"results/{design}/qualified-bank-v6.json"
    if sha(bank_path) != bundle[str(bank_path.relative_to(ROOT))]["sha256"]:
        raise ValueError("original bank differs from frozen program archive")
    bank = read(bank_path)
    prior = read(ROOT / f"out/{design}-transport-bridge-v1/reference/manifest.json")
    spec = {**prior["spec"], "name": f"{design}-bit-activity-v1-reference", "policies": ["random"]}
    config = {"name": f"{design}-bit-activity-v1-remeasurement", "domain": bank["domain"],
              "scope": "new bit metric on fixed programs; no old scales or compatibility claims",
              "max_workers": 18, "cases": fixed_cases(bundle, design)}
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "spec.json", spec)
    write(destination / "config.json", config)
    write(destination / "old-bank.json", bank)
    write(destination / "lineage.json", {"audit_inputs_sha256": sha(archive), "old_bank_sha256": sha(bank_path),
                                        "procedure_sha256": sha(ROOT / "docs/BIT_ACTIVITY_V1.md"),
                                        "driver_sha256": sha(Path(__file__))})
    prepare(ROOT, destination / "spec.json", destination / "reference")
    probe = runpy.run_path(ROOT / "scripts/probe_fixed_cases.py")
    probe["prepare"](destination / "reference", destination / "config.json", destination / "replay")
    write(destination / "freeze.json", {p.name: sha(p) for p in destination.glob("*.json")})
    return {"design": design, "cases": 82, "executed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", choices=DESIGNS, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(plan(args.destination.resolve(), args.design)))
