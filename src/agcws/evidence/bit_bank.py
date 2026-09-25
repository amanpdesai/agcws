"""Read-only verifier for the published bit-activity-v2 evidence format.

Its frozen 0.1 RMSE rules reproduce that archive, not the current 0.05 per-bin gate.
No witness search, simulation, study preparation or provider calls are available.
"""

import argparse
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

from agcws.evaluation.activity.known_bits import CONTRACT
from agcws.studies.targets import SHAPES, diagnostics, distance, qualify, requests


def fixed_cases(calibration_rows, witness_rows):
    """Recover the full frozen program set, including invalid calibration attempts."""
    cases = [{"id": row["id"], "program": row["program"]} for row in calibration_rows
             if row["id"].startswith("calibration-")]
    cases += [{"id": row["id"], "program": row["program"]} for row in witness_rows
              if row["id"].startswith(("development-", "confirmation-"))]
    if len(cases) != 82 or len({c["id"] for c in cases}) != 82:
        raise ValueError("exact 64 calibration and 18 witness programs required")
    return sorted(cases, key=lambda c: c["id"])


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


def checked_trial(trial, target, scale):
    if trial["selected"] is not True or trial["status"] != "MEASURED":
        raise ValueError("qualification cannot filter proposals")
    if trial["valid"] is not True:
        if trial["loss"] is not None:
            raise ValueError("invalid attempt has a score")
        return
    actual = distance(trial["rates"], target, scale)
    if not math.isclose(actual, trial["loss"], rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("saved target error differs")


def fixed_work_requests(low, high, mean, split):
    if split not in ("development", "confirmation") or not low < mean < high:
        raise ValueError("explicit split and nondegenerate calibrated mean required")
    shapes = dict(SHAPES)
    if split == "development":
        shapes.update(activation=(0, 0, 0, 1, 1, 1, 1, 1),
                      deactivation=(1, 1, 1, 0, 0, 0, 0, 0),
                      burst=(0, 0, 1, 1, 0, 0, 0, 0),
                      quiet_interval=(1, 1, 0, 0, 0, 1, 1, 1),
                      alternating=(1, 0, 1, 0, 1, 0, 1, 0),
                      ramp=(0, .14, .29, .43, .57, .71, .86, 1),
                      rise_fall=(0, .5, 1, 1, .5, 0, 0, 0),
                      irregular=(1, 0, .5, 0, 1, 0, .5, 0))
    result = []
    for name, shape in shapes.items():
        if name == "flat_control":
            rates = [mean]*8
        else:
            center = statistics.mean(shape)
            amplitude = min((mean-low)/(center-min(shape)), (high-mean)/(max(shape)-center))
            amplitude *= .9 if split == "development" else 1.0
            rates = [mean+amplitude*(value-center) for value in shape]
        result.append({"id": name, "split": split, "rates": rates,
                       "control": name == "flat_control", "qualified": False,
                       **diagnostics(rates, high-low)})
    return result


def verify(directory):
    inputs = directory / "inputs.json.gz"
    if not inputs.is_file():
        inputs = directory / "calibration/inputs.json.gz"
    with gzip.open(inputs, "rt") as stream:
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
    replay = read("replay/complete.json")
    if replay["charged_slots"] != 82 or len(replay["results"]) != 82:
        raise ValueError("incomplete fixed replay")
    originals = {r["id"]: r for r in replay["results"]}
    cal = calibration(replay["results"])
    if cal != bank["calibration"] or cal != read("qualification/calibration.json"):
        raise ValueError("calibration differs")
    fixed = fixed_work_requests
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
    ids = [r["id"] for r in admission["outcomes"]]
    if len(ids) != 18 or set(ids) != set(targets) or admission["requests"] != 18:
        raise ValueError("incomplete target admission")
    if set(r["id"] for r in attempts) != set(targets):
        raise ValueError("attempts do not cover the declared targets")
    for outcome in admission["outcomes"]:
        target = targets[outcome["id"]]
        rows = [r for r in attempts if r["id"] == outcome["id"]]
        original = [r for r in rows if r["source"] == "fixed-original-witness"]
        if len(original) != 1:
            raise ValueError("one original witness attempt required")
        measured = originals[outcome["id"]]
        profile = measured["measurement"]
        rates = profile["profile"]["window_rates"] if profile["valid"] else None
        if (original[0]["program"] != measured["program"] or original[0]["rates"] != rates
                or original[0]["valid"] != profile["valid"]):
            raise ValueError("original witness does not match replay")
        needed = not original[0]["qualified"] and (target["control"] or target["constant_floor"] > .12)
        if len(rows) != (513 if needed else 1):
            raise ValueError("declared witness budget differs")
        for arm in ("phase-random", "phase-ga"):
            slots = [r["slot"] for r in rows if r["source"] == arm]
            if slots != (list(range(1, 257)) if needed else []):
                raise ValueError("classical proposal axis differs")
        for row in rows:
            if row["source"] != "fixed-original-witness":
                checked_trial(row, target["rates"], cal["scale"])
            result = qualify(target, row, scale=cal["scale"], tolerance=.1, nonflat_margin=.02)
            if any(row[k] != v for k, v in result.items()):
                raise ValueError("qualification arithmetic differs")
        successful = [r for r in rows if r["qualified"]]
        best = min(successful, key=lambda r: (r["witness_error"], r["source"], r.get("slot", 0))) if successful else None
        if (outcome["witness"] != best or outcome["qualified"] != bool(successful)
                or outcome["attempts"] != len(rows)):
            raise ValueError("admitted witness differs")
    if (admission["charged_witness_attempts"] != len(attempts)
            or admission["qualified"] != sum(r["qualified"] for r in admission["outcomes"])
            or admission["task_bank_qualified"] != all(r["qualified"] for r in admission["outcomes"])):
        raise ValueError("admission accounting differs")
    witnesses = {r["id"]: r["witness"] for r in admission["outcomes"]}
    crosses = read("qualification/cross-solves.json")
    pairs = {(r["witness"], r["target"]) for r in crosses}
    expected_pairs = {(w, t) for w, v in witnesses.items() if v is not None for t in targets}
    if pairs != expected_pairs or len(crosses) != len(pairs):
        raise ValueError("incomplete cross-solve matrix")
    for row in crosses:
        error = distance(witnesses[row["witness"]]["rates"], targets[row["target"]]["rates"], cal["scale"])
        if error != row["error"] or row["within_tolerance"] != (error <= .1):
            raise ValueError("cross-solve arithmetic differs")
    published = json.loads((directory / "bank.json").read_text())
    if published != {**bank, "admission": admission, "task_bank_qualified": admission["task_bank_qualified"]}:
        raise ValueError("published bank differs")
    return {"domain": bank["domain"], "verified": True, "qualified": admission["qualified"],
            "attempts": len(attempts), "scope": "offline arithmetic, not waveform resimulation"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(verify(args.directory)))
