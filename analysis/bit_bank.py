"""Freeze analytic new-metric targets, then assess fixed witnesses and CPU searches."""

import argparse
import hashlib
import itertools
import json
import math
import runpy
import statistics
from pathlib import Path

from agcws.config import ROOT
from agcws.nodes.bit_activity import CONTRACT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import distance, qualify, requests


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calibration(rows):
    samples = [r["measurement"] for r in rows if r["id"].startswith("calibration-")]
    if len(samples) != 64:
        raise ValueError("all 64 original calibration attempts required")
    valid = [r for r in samples if r["valid"] is True]
    failures = {}
    for r in samples:
        if r["valid"] is not True:
            failures[r["stage"]] = failures.get(r["stage"], 0)+1
    result = {"proposals": 64, "valid": len(valid), "failure_stages": failures,
              "activity_contract": CONTRACT, "status": "insufficient_valid_calibration"}
    if len(valid) < 32:
        return result
    if any(r["profile"]["activity_contract"] != CONTRACT for r in valid):
        raise ValueError("wrong calibration activity contract")
    bins = sorted(x for r in valid for x in r["profile"]["window_rates"])
    if len(bins) != len(valid)*8 or any(not math.isfinite(x) or x < 0 for x in bins):
        raise ValueError("malformed calibration rates")

    def percentile(fraction):
        index = (len(bins)-1)*fraction
        low, high = math.floor(index), math.ceil(index)
        return bins[low] + (bins[high]-bins[low])*(index-low)

    low, high = percentile(.05), percentile(.95)
    mean = statistics.median(statistics.mean(r["profile"]["window_rates"]) for r in valid)
    return {**result, "low": low, "high": high, "scale": high-low, "median_window_mean": mean,
            "status": "calibrated" if low < mean < high else "degenerate_calibration"}


def verified_replay(root):
    for name, digest in read(root / "freeze.json").items():
        if sha(root / name) != digest:
            raise ValueError("frozen input changed")
    lineage = read(root / "lineage.json")
    if lineage["procedure_sha256"] != sha(ROOT / "docs/BIT_ACTIVITY_V1.md"):
        raise ValueError("qualification procedure changed")
    if lineage["alignment_correction_sha256"] != sha(ROOT / "docs/BIT_ACTIVITY_ALIGNMENT_V2.md"):
        raise ValueError("alignment correction changed")
    manifest = read(root / "replay/manifest.json")
    if (manifest["measurement"] != verify_inputs(ROOT, root / "reference")
            or manifest["driver_sha256"] != sha(ROOT / "scripts/probe_fixed_cases.py")
            or read(root / "replay/freeze.json")["manifest_sha256"] != sha(root / "replay/manifest.json")):
        raise ValueError("replay runtime or driver changed")
    complete = read(root / "replay/complete.json")
    cases = read(root / "config.json")["cases"]
    if len(complete["results"]) != 82 or complete["charged_slots"] != 82:
        raise ValueError("incomplete fixed replay")
    for row, case in zip(complete["results"], cases, strict=True):
        if row["id"] != case["id"] or row["program"] != case["program"]:
            raise ValueError("replayed program changed")
        if row != read(root / "replay/panel" / row["id"] / "result.json"):
            raise ValueError("replay checkpoint differs")
        measurement = row["measurement"]
        if measurement["valid"] is True and measurement["profile"]["activity_contract"] != CONTRACT:
            raise ValueError("old measurement reused")
    return complete["results"], manifest["measurement"]


def plan(root):
    rows, manifest = verified_replay(root)
    cal = calibration(rows)
    destination = root / "qualification"
    destination.mkdir(exist_ok=False)
    write(destination / "calibration.json", cal)
    if cal["status"] != "calibrated":
        write(destination / "failure.json", cal)
        return cal
    domain = manifest["spec"]["domain"]
    fixed = runpy.run_path(ROOT / "scripts/prepare_target_bank.py")["fixed_work_requests"]
    bank = {"procedure": "docs/BIT_ACTIVITY_V1.md", "activity_contract": CONTRACT, "domain": domain,
            "calibration": cal, "measurement_fingerprint": manifest["measurement_fingerprint"],
            "splits": {}, "full_study_ready": False}
    for split in ("development", "confirmation"):
        targets = (fixed(cal["low"], cal["high"], cal["median_window_mean"], split)
                   if domain in ("aes-temporal", "dma-temporal")
                   else requests(cal["low"], cal["high"], split=split))
        bank["splits"][split] = {"requests": targets, "pairwise_distances": [
            {"left": a["id"], "right": b["id"], "distance": distance(a["rates"], b["rates"], cal["scale"])}
            for a, b in itertools.combinations(targets, 2)]}
    # Freeze requested vectors before reading any witness measurements for scoring.
    write(destination / "requested-bank.json", bank)
    write(destination / "target-freeze.json", {"requested_bank_sha256": sha(destination / "requested-bank.json"),
          "calibration_sha256": sha(destination / "calibration.json"), "driver_sha256": sha(Path(__file__)),
          "replay_complete_sha256": sha(root / "replay/complete.json")})
    by_id = {r["id"]: r for r in rows}
    initial, planned = [], []
    for split, part in bank["splits"].items():
        missed = {}
        for target in part["requests"]:
            name = f"{split}-{target['id']}"
            row = by_id[name]
            measurement = row["measurement"]
            outcome = qualify(target, {**measurement, "rates": measurement["profile"]["window_rates"]
                              if measurement["valid"] else None}, scale=cal["scale"], tolerance=.1, nonflat_margin=.02)
            initial.append({"id": name, "charged_slots": 1, **outcome, "measurement": measurement,
                            "program": row["program"]})
            if not outcome["qualified"] and (target["control"] or target["constant_floor"] > .12):
                missed[name] = target["rates"]
        if missed:
            spec = {**manifest["spec"], "name": f"{domain}-bit-witness-v1-{split}", "targets": missed,
                    "seeds": [7300 if split == "development" else 7400],
                    "policies": ["phase-random", "phase-ga"], "budget": 256, "batch_size": 2,
                    "scale": cal["scale"], "tolerance": .1, "stop_on_success": False,
                    "max_workers": 18, "image": manifest["runtime"]["image_id"]}
            path = destination / f"{split}.json"
            write(path, spec)
            prepare(ROOT, path, destination / split)
            planned.append(split)
    ensure(destination / "initial-witnesses.json", initial)
    return {"domain": domain, "initial_qualified": sum(r["qualified"] for r in initial),
            "classical_panels_prepared": planned, "executed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(plan(args.root.resolve())))
