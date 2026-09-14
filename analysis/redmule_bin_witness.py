"""Freeze nonadaptive per-bin candidates from marginal measured job activity."""

import argparse
import hashlib
import math
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.storage import read, write


def make_config(probe, bank):
    rows = {row["id"]: row for row in read(probe / "complete.json")["results"]}
    if len(rows) != 18 or not all(row["measurement"]["valid"] for row in rows.values()):
        raise ValueError("complete eighteen-case diagnostic required")
    measurement = read(probe / "manifest.json")["measurement"]
    if bank["calibration"]["measurement_fingerprint"] != measurement["measurement_fingerprint"]:
        raise ValueError("bank and diagnostic runtime fingerprints differ")
    rounds = {"floor": math.floor, "nearest": lambda x: math.floor(x+.5), "ceil": math.ceil}
    cases = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            for size in (4, 8, 16):
                for pattern in ("zeros", "alternating", "random"):
                    left, right = [rows[f"size{size}-{pattern}-x{mult}"] for mult in (1, 2)]
                    jobs = [sum(p["jobs"] for p in r["program"]["phases"]) for r in (left, right)]
                    marginal = (sum(right["measurement"]["rates"])-sum(left["measurement"]["rates"]))*32768/(jobs[1]-jobs[0])
                    if not math.isfinite(marginal) or marginal <= 0:
                        raise ValueError("positive measured marginal activity required")
                    for name, rounding in rounds.items():
                        counts = [max(0, rounding((rate-2)*32768/marginal)) for rate in request["rates"]]
                        cases.append({"id": f"{split}--{request['id']}--{size}-{pattern}-{name}",
                                      "program": {"size": size, "pattern": pattern, "data_seed": 7500,
                                                  "phases": [{"start": i*32768+2048, "duration": 1, "jobs": count}
                                                             for i, count in enumerate(counts) if count]}})
    if len(cases) != 486:
        raise ValueError("eighteen requests with 27 proposals each required")
    return {"name": "redmule-long-bin-witness-v1", "domain": "redmule-temporal-long",
            "scope": "expert feasibility constructor; all failures retained; not policy evidence",
            "max_workers": 18, "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bank = read(args.bank)
    bridge = read(args.calibration / "replay-audit.json")
    current = verify_inputs(ROOT, args.calibration)
    if (bridge["cases"] != 64 or not bridge["exact_integer_activity_match"]
            or bridge["old_measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]
            or bridge["new_measurement_fingerprint"] != current["measurement_fingerprint"]):
        raise ValueError("exact calibration bridge required before reusing requested vectors")
    bank["calibration"]["measurement_fingerprint"] = current["measurement_fingerprint"]
    bank["runtime_bridge"] = {"source_bank_sha256": hashlib.sha256(args.bank.read_bytes()).hexdigest(),
                              "audit": bridge, "scope": "unchanged requests, not admitted targets"}
    config = make_config(args.probe, bank)
    write(args.output.with_suffix(".bank.json"), bank)
    write(args.output, config)
