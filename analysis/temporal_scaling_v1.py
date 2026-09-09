"""Reconstruct qualification proposals, targets and compact CPU evidence offline."""

import argparse
import collections
import math
import random
from pathlib import Path

from agcws.provenance import file_sha256
from analysis.ibex_depth_v1 import check_prefix_arithmetic, check_trial, value
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.storage import read
from experiments.temporal_scaling_v1.baselines import phase_random
from experiments.temporal_scaling_v1.smoke import propose
from experiments.temporal_scaling_v1.targets import match_request, witnessed_target


def check_loss(trial, rates, scale):
    expected = (
        math.sqrt(
            sum(
                ((a - b) / scale) ** 2
                for a, b in zip(trial["rates"], rates, strict=True)
            )
            / len(rates)
        )
        if trial["valid"]
        else None
    )
    if (expected is None and trial["loss"] is not None) or (
        expected is not None
        and (
            trial["loss"] is None
            or not math.isclose(trial["loss"], expected, rel_tol=1e-12, abs_tol=1e-12)
        )
    ):
        raise ValueError("trial loss differs")


def audit(root):
    manifest = read(root / "manifest.json")
    if file_sha256(root / "parent_manifest.json") != manifest["parent_sha256"]:
        raise ValueError("parent manifest differs")
    if read(root / "complete.json") != {
        "witness_proposals": 12,
        "search_slots": 72,
        "cells": 6,
    }:
        raise ValueError("incomplete qualification")
    rng = random.Random(manifest["witness_seed"])
    eligible, witnesses = [], []
    for slot in range(1, manifest["witness_proposals"] + 1):
        trial = read(root / "witnesses" / f"{slot:03}.json")
        if trial["program"] != phase_random(rng, slot) or trial["slot"] != slot:
            raise ValueError("witness generator differs")
        check_trial(root, trial, manifest)
        check_loss(trial, [0.0] * 8, manifest["scale"])
        witnesses.append(trial)
        if trial["valid"]:
            result = value(root, f"evaluations/{trial['cache_id']}/result.json")
            target = witnessed_target(
                trial["program"],
                result,
                manifest["measurement_fingerprint"],
                manifest["scale"],
            )
            if (max(target["target_rates"]) - min(target["target_rates"])) / manifest[
                "scale"
            ] >= manifest["minimum_normalized_range"]:
                eligible.append(target)
    targets = read(root / "targets.json")
    if (
        len(targets) != manifest["target_count"]
        or targets != eligible[: manifest["target_count"]]
    ):
        raise ValueError("target selection differs from predeclared rule")
    summaries, operators = [], collections.Counter()
    for index, target in enumerate(targets):
        for arm in manifest["arms"]:
            rng, history = random.Random(manifest["search_seed"]), []
            cell = root / "panel" / str(index) / arm
            for start in range(1, manifest["budget"] + 1, 2):
                batch = []
                for slot in (start, start + 1):
                    program, operator = propose(arm, rng, slot, history)
                    trial = read(cell / f"{slot:03}.json")
                    if (
                        trial["slot"] != slot
                        or trial["program"] != program
                        or trial["operator"] != operator
                    ):
                        raise ValueError("proposal or feedback timing differs")
                    check_trial(root, trial, manifest)
                    check_loss(trial, target["target_rates"], manifest["scale"])
                    operators[operator["operator"]] += 1
                    batch.append(trial)
                history.extend(batch)
            summary = read(cell / "summary.json")
            if summarize(history, manifest["budget"], manifest["tolerance"]) != summary:
                raise ValueError("cell summary differs")
            check_prefix_arithmetic(history, summary, manifest["tolerance"])
            summaries.append(
                {
                    "target": index,
                    "arm": arm,
                    **summary,
                    "validity": dict(
                        collections.Counter(
                            "VALID" if t["valid"] else t["stage"] for t in history
                        )
                    ),
                }
            )
    matches = []
    for request in manifest["requests"]:
        spec = request["spec"]
        if (spec["horizon_cycles"], spec["bins"]) != (200000, 8):
            matches.append(
                {
                    "request_id": request["id"],
                    "status": "unsupported-measurement-configuration",
                }
            )
        else:
            candidates = [
                match_request(request, t, manifest["tolerance"]) for t in eligible
            ]
            best = min(candidates, key=lambda x: (x["loss"], x["witness"]))
            matches.append(
                {
                    **best,
                    "status": "witnessed-within-tolerance"
                    if best["qualified"]
                    else "unqualified-no-matching-witness",
                }
            )
    return {
        "complete": True,
        "scope": "CPU qualification only; one seed and two witness-derived targets, not efficacy evidence",
        "witness_proposals": len(witnesses),
        "valid_witnesses": sum(t["valid"] for t in witnesses),
        "eligible_nonflat_witnesses": len(eligible),
        "search_slots": 72,
        "cells": summaries,
        "operators": dict(operators),
        "request_qualification": matches,
        "model_calls": 0,
        "verification": "compact CPU/reference/window/metric reconstruction, not waveform replay",
    }


def verify(root):
    index = read(root / "sha256.json")
    actual = {
        str(p.relative_to(root)): file_sha256(p)
        for p in root.rglob("*")
        if p.is_file() and p.name != "sha256.json"
    }
    if index != actual:
        raise ValueError("archive file set or checksum differs")
    manifest = read(root / "manifest.json")
    for name, sha in manifest["sources"].items():
        path = root / "sources" / name
        if (
            not path.resolve().is_relative_to(root.resolve())
            or file_sha256(path) != sha
        ):
            raise ValueError("source snapshot differs")
        if file_sha256(Path(name)) != sha:
            raise ValueError("auditor is importing changed producer sources")
    if audit(root) != read(root / "summary.json"):
        raise ValueError("aggregate differs")
    return {
        "complete": True,
        "search_slots": 72,
        "witness_proposals": 12,
        "files": len(index),
    }


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--archive", type=Path, required=True)
    print(verify(args.parse_args().archive))
