"""Independent geometry and witness checks; no model or simulator invocation."""

import argparse
import gzip
import hashlib
import itertools
import json
import math
import statistics
from pathlib import Path

from agcws.pipeline.storage import write

DESIGNS = ("aes", "dma", "mesh", "ibex", "redmule")


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


def difficulty(repo, design, target, rates, scale, inputs):
    version, seed = (5, 8503) if design in ("aes", "dma") else (4, 8502)
    root = repo / f"out/{design}-bank-smoke-v{version}/run/panel/{target}/{seed}"
    records = []
    for arm in ("phase-random", "phase-ga"):
        directory = root / arm
        summary = inputs.read(directory / "complete.json")
        paths = [directory / f"batches/{slot:03}/trials.json" for slot in range(1, 17, 2)]
        trials = [trial for path in paths for trial in inputs.read(path)]
        if [t["slot"] for t in trials] != list(range(1, 17)):
            raise ValueError(f"incomplete smoke slots: {directory}")
        best, curve, hits = math.inf, [], []
        for trial in trials:
            if trial["valid"]:
                loss = rmse(trial["rates"], rates, scale)
                if not math.isclose(loss, trial["loss"], abs_tol=1e-12):
                    raise ValueError(f"trial loss mismatch: {directory}/{trial['slot']}")
                best = min(best, loss)
                if loss <= .1:
                    hits.append(trial["slot"])
            curve.append(best)
        if any(not math.isfinite(x) for x in curve):
            raise ValueError(f"initialization has no finite score: {directory}")
        auc = sum((a+b)/2 for a, b in itertools.pairwise(curve))
        if not math.isclose(auc, summary["auc"], abs_tol=1e-12):
            raise ValueError(f"summary AUC mismatch: {directory}")
        records.append({"policy": arm, "seed": seed, "budget": 16,
                        "valid_slots": sum(t["valid"] for t in trials),
                        "first_hit": hits[0] if hits else None,
                        "evaluations_to_target": hits[0] if hits else 16,
                        "right_censored": not hits, "solved": bool(hits),
                        "auc": auc, "final_error": curve[-1],
                        "source_summary": str((directory / "complete.json").relative_to(repo)),
                        "source_sha256": {str(p.relative_to(repo)): inputs.sha(p)
                                          for p in [directory / "complete.json", *paths]},
                        "scope": "one exposed engineering seed; descriptive difficulty, not inference"})
    return records


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


def geometry(requests, scale, tolerance=.1):
    pairs = []
    for left, right in itertools.combinations(requests, 2):
        distance = rmse(left["rates"], right["rates"], scale)
        pairs.append({"left": left["key"], "right": right["key"],
                      "distance": distance, "unconstrained_tolerance_balls_overlap": distance <= 2*tolerance,
                      "note": "geometric overlap does not prove a legal workload lies in the intersection"})
    return pairs


def audit(repo, inputs=None):
    inputs = Inputs(repo) if inputs is None else inputs
    designs = []
    for name in DESIGNS:
        bank_path = repo / f"results/{name}/qualified-bank-v6.json"
        replay_path = repo / ("out/ibex-bank-admission-v5/run/complete.json" if name == "ibex"
                              else f"out/{name}-runtime-replay-v5/replay/complete.json")
        bank, replay = inputs.read(bank_path), inputs.read(replay_path)
        scale = bank["calibration"]["scale"]
        witnesses = {r["id"]: r for r in replay["results"]}
        requests, rows = [], []
        for split, part in sorted(bank["splits"].items()):
            for request in part["requests"]:
                key = f"{split}-{request['id']}"
                requests.append({**request, "key": key})
                witness = witnesses[request["witness_case"]]
                measured = witness["measurement"]
                if not measured["valid"] or measured["cache_id"] != request["witness_cache_id"]:
                    raise ValueError(f"witness identity/validity mismatch: {name}/{key}")
                achieved = measured["profile"]["window_rates"]
                error = rmse(achieved, request["rates"], scale)
                descriptors = shape(request["rates"], scale)
                if (not math.isclose(error, request["witness_error"], abs_tol=1e-12)
                        or not math.isclose(descriptors["constant_floor"], request["constant_floor"], abs_tol=1e-12)):
                    raise ValueError(f"published metric differs: {name}/{key}")
                if error > .1 or (not request["control"] and descriptors["constant_floor"] <= .12):
                    raise ValueError(f"original admission gate fails: {name}/{key}")
                rows.append({"key": key, "split": split, "family": request["id"], "control": request["control"],
                             "target": request["rates"], "target_shape": descriptors,
                             "witness_rates": achieved, "witness_error": error,
                             "witness_shape": shape(achieved, scale),
                             "witness_program_sha256": hashlib.sha256(json.dumps(witness["program"], sort_keys=True).encode()).hexdigest(),
                             "witness_profile": measured["profile"],
                             "baseline_smoke_difficulty": difficulty(repo, name, key, request["rates"], scale, inputs),
                             "witness_headroom_to_tolerance": .1-error})
        for row in rows:
            row["other_requests_solved_by_same_witness"] = [r["key"] for r in requests
                if r["key"] != row["key"] and rmse(row["witness_rates"], r["rates"], scale) <= .1]
        pairs = geometry(requests, scale)
        designs.append({"design": name, "scale": scale, "targets": rows, "pairwise": pairs,
                        "sources": {str(p.relative_to(repo)): inputs.sha(p)
                                    for p in (bank_path, replay_path)},
                        "within_confirmation_overlap_pairs": [p for p in pairs
                            if p["left"].startswith("confirmation-") and p["right"].startswith("confirmation-")
                            and p["unconstrained_tolerance_balls_overlap"]]})
    return {"scope": "initial independent geometry/witness audit; not complete task-quality certification",
            "tolerance": .1, "simulation_calls": 0, "llm_calls": 0,
            "existing_banks_changed": False, "designs": designs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, help="offline captured JSON.gz inputs; no out/ required")
    parser.add_argument("--capture-inputs", type=Path, help="write immutable compact inputs for reproduction")
    args = parser.parse_args()
    bundle = None
    if args.inputs:
        with gzip.open(args.inputs, "rt") as stream:
            bundle = json.load(stream)
    inputs = Inputs(args.repo, bundle)
    write(args.output, audit(args.repo, inputs))
    if args.capture_inputs:
        with args.capture_inputs.open("xb") as stream:
            stream.write(gzip.compress(json.dumps(inputs.records, sort_keys=True).encode(), mtime=0))
