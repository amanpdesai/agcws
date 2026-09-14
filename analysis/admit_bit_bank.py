"""Audit every declared witness attempt before admitting a new-metric bank."""

import argparse
import json
import math
from pathlib import Path

from bit_bank import calibration, sha, verified_replay

from agcws.config import ROOT
from agcws.nodes.bit_activity import CONTRACT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import summarize
from agcws.pipeline.storage import ensure, read
from agcws.pipeline.targets import distance, qualify


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


def search_attempts(root, targets, scale):
    manifest = verify_inputs(ROOT, root)
    spec = manifest["spec"]
    split = root.name
    if (spec["policies"] != ["phase-random", "phase-ga"] or spec["budget"] != 256
            or spec["batch_size"] != 2 or spec["stop_on_success"] is not False
            or spec["targets"] != targets or spec["scale"] != scale
            or spec["seeds"] != [7300 if split == "development" else 7400]):
        raise ValueError("qualification search differs from declaration")
    complete = read(root / "complete.json")
    attempts, summaries = [], []
    for target in targets:
        for seed in spec["seeds"]:
            for arm in spec["policies"]:
                cell = root / "panel" / target / str(seed) / arm
                trials = []
                for batch in sorted((cell / "batches").iterdir()):
                    proposals, saved = read(batch / "proposals.json"), read(batch / "trials.json")
                    if len(proposals) != len(saved) or any(
                        any(t.get(k) != v for k, v in p.items())
                        for p, t in zip(proposals, saved, strict=True)
                    ):
                        raise ValueError("proposal and trial differ")
                    trials.extend(saved)
                for trial in trials:
                    checked_trial(trial, targets[target], scale)
                    if trial["valid"] is True:
                        cached = read(root / "cache" / trial["cache_id"] / "result.json")
                        profile = cached["profile"]
                        if (cached["valid"] is not True or profile["activity_contract"] != CONTRACT
                                or trial["rates"] != profile["window_rates"]):
                            raise ValueError("trial differs from measured cache")
                    attempts.append({"id": target, "source": arm, "seed": seed, **trial})
                summary = summarize(trials, 256, .1)
                saved = read(cell / "complete.json")
                if any(saved[k] != v for k, v in summary.items()):
                    raise ValueError("cell summary differs")
                summaries.append(saved)
    if (complete["summaries"] != summaries or complete["slots"] != len(attempts)
            or complete["cells"] != len(summaries)):
        raise ValueError("panel accounting differs")
    if complete["liability_usd"] != 0:
        raise ValueError("CPU-only qualification incurred provider liability")
    return attempts


def audit(root):
    rows, measurement = verified_replay(root)
    directory = root / "qualification"
    freeze = read(directory / "target-freeze.json")
    for key, path in (("requested_bank_sha256", directory / "requested-bank.json"),
                      ("calibration_sha256", directory / "calibration.json"),
                      ("driver_sha256", Path(__file__).with_name("bit_bank.py")),
                      ("replay_complete_sha256", root / "replay/complete.json")):
        if freeze[key] != sha(path):
            raise ValueError("target freeze changed")
    bank = read(directory / "requested-bank.json")
    if bank["calibration"] != calibration(rows):
        raise ValueError("calibration cannot be reproduced")
    if bank["measurement_fingerprint"] != measurement["measurement_fingerprint"]:
        raise ValueError("bank measurement differs")
    initial = read(directory / "initial-witnesses.json")
    by_id = {r["id"]: r for r in rows}
    attempts, outcomes = [], []
    scale = bank["calibration"]["scale"]
    for split, part in bank["splits"].items():
        missed = {}
        candidates = {}
        for target in part["requests"]:
            name = f"{split}-{target['id']}"
            original = by_id[name]
            result = original["measurement"]
            witness = {**result, "rates": result["profile"]["window_rates"] if result["valid"] else None}
            outcome = qualify(target, witness, scale=scale, tolerance=.1, nonflat_margin=.02)
            saved = next(r for r in initial if r["id"] == name)
            if (saved["measurement"] != result or saved["program"] != original["program"]
                    or any(saved[k] != v for k, v in outcome.items())):
                raise ValueError("initial witness evidence changed")
            row = {"id": name, "source": "fixed-original-witness", "program": original["program"],
                   "valid": result["valid"], "rates": witness["rates"], **outcome}
            candidates[name] = [row]
            attempts.append(row)
            if not outcome["qualified"] and (target["control"] or target["constant_floor"] > .12):
                missed[name] = target["rates"]
        if missed:
            extra = search_attempts(directory / split, missed, scale)
            for row in extra:
                target = next(t for t in part["requests"] if row["id"] == f"{split}-{t['id']}")
                outcome = qualify(target, row, scale=scale, tolerance=.1, nonflat_margin=.02)
                row.update(outcome)
                candidates[row["id"]].append(row)
                attempts.append(row)
        for name, choices in candidates.items():
            successful = [r for r in choices if r["qualified"]]
            best = min(successful, key=lambda r: (r["witness_error"], r["source"], r.get("slot", 0))) if successful else None
            outcomes.append({"id": name, "qualified": bool(successful), "attempts": len(choices),
                             "witness": best, "failure_reasons": sorted({
                                 reason for r in choices for reason in r["reasons"]}) if not best else []})
    cross_solves = []
    for source in outcomes:
        if source["witness"] is None:
            continue
        for split, part in bank["splits"].items():
            for target in part["requests"]:
                error = distance(source["witness"]["rates"], target["rates"], scale)
                cross_solves.append({"witness": source["id"], "target": f"{split}-{target['id']}",
                                     "error": error, "within_tolerance": error <= .1})
    result = {"activity_contract": CONTRACT, "domain": bank["domain"],
              "measurement_fingerprint": bank["measurement_fingerprint"],
              "qualified": sum(r["qualified"] for r in outcomes), "requests": 18,
              "charged_witness_attempts": len(attempts), "outcomes": outcomes,
              "task_bank_qualified": all(r["qualified"] for r in outcomes),
              "full_study_ready": False, "scope": "CPU target qualification, not provider readiness"}
    ensure(directory / "audited-attempts.json", attempts)
    ensure(directory / "cross-solves.json", cross_solves)
    ensure(directory / "admission.json", result)
    return {k: v for k, v in result.items() if k != "outcomes"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.root.resolve())))
