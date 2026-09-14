"""Audit the fixed RedMulE operand panel without relaxing qualification."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import error, key
from agcws.pipeline.redmule import RedmuleTemporal
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def analyze(root):
    manifest = read(root / "probe/manifest.json")
    if read(root / "probe/freeze.json")["manifest_sha256"] != hashlib.sha256((root / "probe/manifest.json").read_bytes()).hexdigest():
        raise ValueError("manifest changed")
    if manifest["measurement"] != verify_inputs(ROOT, root / "reference"):
        raise ValueError("measurement changed")
    parents = read(root / "parent-reports.json")
    cases = runpy.run_path(ROOT / "analysis/redmule_operand_probe.py")["cases"](parents)
    if cases != manifest["config"]["cases"]:
        raise ValueError("frozen proposals differ")
    complete = read(root / "probe/complete.json")
    if complete["charged_slots"] != 354 or len(complete["results"]) != 354:
        raise ValueError("complete panel required")
    design = RedmuleTemporal()
    rows = {}
    for case, row in zip(cases, complete["results"], strict=True):
        if row["id"] != case["id"] or row["program"] != case["program"]:
            raise ValueError("case differs")
        result = row["measurement"]
        identifier = key({"program": case["program"], "measurement": manifest["measurement"]["measurement_fingerprint"]})
        if result["cache_id"] != identifier or read(root / "probe/cache" / identifier / "result.json") != result:
            raise ValueError("cache differs")
        if read(root / "probe/panel" / row["id"] / "result.json") != row:
            raise ValueError("checkpoint differs")
        if result["valid"]:
            paths = list((root / "probe/cache" / identifier).glob("attempt-*/activity.json"))
            if len(paths) != 1 or not design.completed(paths[0].parent)["valid"]:
                raise ValueError("functional evidence absent")
            samples = read(paths[0])["per_cycle_toggles"]
            rates = [sum(samples[i*8192:(i+1)*8192])/8192 for i in range(8)]
            if len(samples) != 65536 or rates != result["rates"] or rates != result["profile"]["window_rates"]:
                raise ValueError("activity does not reconstruct")
        elif result.get("rates") is not None:
            raise ValueError("invalid proposal scored")
        rows[row["id"]] = row
    compare = runpy.run_path(ROOT / "analysis/runtime_replay.py")["comparable"]
    for parent in parents:
        if compare(rows[parent["id"]+"-replay"]["measurement"]) != compare(parent["measurement"]):
            raise ValueError("parent replay changed")
    bank = read(root / "parent-manifest.json")["bank"]
    reports = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            name = f"{split}-{request['id']}"
            candidates = [r for n, r in rows.items() if n.startswith(name+"-")]
            valid = [r for r in candidates if r["measurement"]["valid"]]
            best = min(valid, key=lambda r: (error(r["measurement"]["rates"], request["rates"], bank["calibration"]["scale"]), r["id"])) if valid else None
            result = best["measurement"] if best else {"valid": False}
            reports.append({"id": name, "control": request["control"], "charged_slots": len(candidates),
                            "witness_case": best["id"] if best else None,
                            **qualify(request, result, scale=bank["calibration"]["scale"], tolerance=.1, nonflat_margin=.02)})
    return {"scope": "operand qualification diagnostic; not full-bank admission or policy inference",
            "parent_replays_exact": True, "charged_slots": 354,
            "valid": sum(r["measurement"]["valid"] for r in rows.values()), "reports": reports}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, analyze(args.directory))
