"""Read-only benchmark geometry and captured-input calibration checks."""

import argparse
import hashlib
import itertools
import json
import math
import statistics
from pathlib import Path


def verify_trials(trials, target, scale):
    """Recompute recorded losses without relying on policy validity summaries."""
    for trial in trials:
        if type(trial["valid"]) is not bool:
            raise ValueError("malformed validity")
        if not trial["valid"]:
            if trial["loss"] is not None:
                raise ValueError("invalid trial has a score")
            continue
        expected = rmse(trial["rates"], target, scale)
        if not math.isclose(expected, trial["loss"], abs_tol=1e-12):
            raise ValueError("trial loss differs from measured rates")
    return len(trials)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="JSON with requests[{key,rates}], scale, tolerance")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    raw = args.input.read_bytes()
    data = json.loads(raw)
    result = {"version": 1, "input_sha256": hashlib.sha256(raw).hexdigest(),
              "metric": "normalized-rmse geometry; not a per-bin acceptance decision",
              "shapes": [{"key": r["key"], **shape(r["rates"], data["scale"])}
                         for r in data["requests"]],
              "pairs": geometry(data["requests"], data["scale"], data["tolerance"])}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"requests": len(result["shapes"]), "pairs": len(result["pairs"])}))


class Inputs:
    def __init__(self, repo, bundle=None):
        self.repo = repo
        self.records = {} if bundle is None else bundle
        self.offline = bundle is not None
        for record in self.records.values():
            digest = hashlib.sha256(json.dumps(record["data"], sort_keys=True).encode()).hexdigest()
            if digest != record["canonical_sha256"]:
                raise ValueError("captured input content hash mismatch")

    def read(self, path):
        key = str(path.relative_to(self.repo))
        if self.offline:
            return self.records[key]["data"]
        raw = path.read_bytes()
        self.records[key] = {"sha256": hashlib.sha256(raw).hexdigest(), "data": json.loads(raw)}
        self.records[key]["canonical_sha256"] = hashlib.sha256(
            json.dumps(self.records[key]["data"], sort_keys=True).encode()).hexdigest()
        return self.records[key]["data"]

    def sha(self, path):
        return self.records[str(path.relative_to(self.repo))]["sha256"]


def rmse(left, right, scale):
    if len(left) != 8 or len(right) != 8 or not math.isfinite(scale) or scale <= 0:
        raise ValueError("eight bins and finite positive scale required")
    if any(not math.isfinite(v) for v in (*left, *right)):
        raise ValueError("finite observations required")
    return math.sqrt(sum((a-b)**2 for a, b in zip(left, right, strict=True))/8)/scale


def shape(values, scale):
    low, high, mean = min(values), max(values), statistics.mean(values)
    differences = [b-a for a, b in itertools.pairwise(values)]
    return {"mean": mean, "span_over_scale": (high-low)/scale,
            "constant_floor": rmse(values, [mean]*8, scale),
            "total_variation_over_scale": sum(abs(x) for x in differences)/scale,
            "up_transitions": sum(x > 0 for x in differences),
            "down_transitions": sum(x < 0 for x in differences),
            "peak_bins_zero_based": [i for i, x in enumerate(values) if x == high],
            "fraction_above_own_midrange": sum(x > (low+high)/2 for x in values)/8}


def calibration_check(rows, published):
    samples = [r["measurement"] for r in rows if r["id"].startswith("calibration-")]
    if len(samples) != 64:
        raise ValueError("all 64 calibration attempts required")
    valid = [r for r in samples if r["valid"]]
    bins = sorted(x for r in valid for x in r["profile"]["window_rates"])
    if len(valid) < 32:
        raise ValueError("insufficient valid calibration")

    def percentile(p):
        index = (len(bins)-1)*p
        left, right = math.floor(index), math.ceil(index)
        return bins[left] + (bins[right]-bins[left])*(index-left)

    low, high = percentile(.05), percentile(.95)
    failures = {}
    for r in samples:
        if not r["valid"]:
            failures[r["stage"]] = failures.get(r["stage"], 0) + 1
    result = {"proposals": 64, "valid": len(valid), "low": low, "high": high,
              "scale": high-low, "failure_stages": failures,
              "median_window_mean": statistics.median(statistics.mean(r["profile"]["window_rates"]) for r in valid)}
    for field in ("low", "high", "scale", "median_window_mean"):
        if not math.isclose(result[field], published[field], abs_tol=1e-12):
            raise ValueError(f"calibration {field} differs")
    if result["valid"] != published["valid"] or failures != published["failure_stages"]:
        raise ValueError("calibration validity differs")
    return result


def geometry(requests, scale, tolerance=.1):
    pairs = []
    for left, right in itertools.combinations(requests, 2):
        distance = rmse(left["rates"], right["rates"], scale)
        pairs.append({"left": left["key"], "right": right["key"],
                      "distance": distance, "unconstrained_tolerance_balls_overlap": distance <= 2*tolerance,
                      "note": "geometric overlap does not prove a legal workload lies in the intersection"})
    return pairs
