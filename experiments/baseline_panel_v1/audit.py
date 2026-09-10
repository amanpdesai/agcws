"""Reconstruct all target selection, policy trajectories and descriptive metrics."""

import math
import random
import statistics

from analysis.ibex_depth_v1 import check_trial
from analysis.temporal_scaling_v1 import check_loss
from experiments.baseline_panel_v1.policies import Control, witness_program
from experiments.baseline_panel_v1.study import choose, identity
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.storage import read


def metrics(trials, budget, tolerance):
    # A numeric view for historical curve integration; retain original tri-state records.
    numeric = [{**t, "valid": t["valid"] is True} for t in trials]
    result = summarize(numeric, budget, tolerance)
    result.update(
        filtered=sum(t["status"] == "FILTERED" for t in trials),
        selected_evaluations=sum(t["status"] == "MEASURED" for t in trials),
        cache_hits=sum(bool(t.get("cache_hit")) for t in trials),
    )
    return result


def describe(cells, manifest):
    by_key = {(c["target"], c["seed"], c["arm"]): c for c in cells}
    reports = {
        key: metrics(c["trials"], manifest["budget"], manifest["tolerance"])
        for key, c in by_key.items()
    }
    arms = {}
    for arm in manifest["arms"]:
        selected = [r for k, r in reports.items() if k[2] == arm]
        arms[arm] = {
            "cells": len(selected),
            "mean_auc": statistics.mean(r["auc"] for r in selected),
            "solves": sum(r["solved"] for r in selected),
            "mean_censored_slots": statistics.mean(
                r["evaluations_to_target"] for r in selected
            ),
            "valid_measured": sum(r["valid_slots"] for r in selected),
            "selected_evaluations": sum(r["selected_evaluations"] for r in selected),
            "filtered": sum(r["filtered"] for r in selected),
        }
    equal_valid = []
    targets = sorted({c["target"] for c in cells})
    for target in targets:
        for seed in manifest["seeds"]:
            histories = {
                a: [t for t in by_key[target, seed, a]["trials"] if t["valid"] is True]
                for a in manifest["arms"]
            }
            count = min(len(h) for h in histories.values())
            equal_valid.append(
                {
                    "target": target,
                    "seed": seed,
                    "common_valid_count": count,
                    "best_errors": {
                        a: min(t["loss"] for t in h[:count]) if count else None
                        for a, h in histories.items()
                    },
                }
            )
    differences = [
        {
            "seed": seed,
            "ridge_minus_pool_auc": statistics.mean(
                reports[target, seed, "ridge-screen"]["auc"]
                - reports[target, seed, "gest-pool4"]["auc"]
                for target in targets
            ),
        }
        for seed in manifest["seeds"]
    ]
    return {
        "complete": True,
        "cells": len(cells),
        "proposals": sum(len(c["trials"]) for c in cells),
        "arms": arms,
        "matched_seed_differences_descriptive_only": differences,
        "equal_valid_secondary": equal_valid,
        "cell_metrics": [
            {"target": k[0], "seed": k[1], "arm": k[2], **r}
            for k, r in sorted(reports.items())
        ],
        "model_calls": 0,
        "scope": "two-seed development, not inference or held-out confirmation",
    }


def audit(archive):
    manifest = identity(archive)
    witnesses = read(archive / "witnesses.json")
    expected_witness_keys = {
        (c["name"], i)
        for c in manifest["constructors"]
        for i in range(1, c["count"] + 1)
    }
    if (
        len(witnesses) != len(expected_witness_keys)
        or {(t["constructor"], t["slot"]) for t in witnesses} != expected_witness_keys
    ):
        raise ValueError("construction attempts missing or duplicated")
    for spec in manifest["constructors"]:
        rng = random.Random(spec["seed"])
        group = [t for t in witnesses if t["constructor"] == spec["name"]]
        if [t["slot"] for t in group] != list(range(1, spec["count"] + 1)):
            raise ValueError("construction ordering differs")
        for trial in group:
            if witness_program(spec["name"], rng, trial["slot"]) != trial["program"]:
                raise ValueError("witness generation differs")
            check_trial(archive, trial, manifest)
            check_loss(trial, [0.0] * 8, manifest["scale"])
    targets = choose(witnesses, manifest)
    if targets != read(archive / "targets.json"):
        raise ValueError("target selection differs")
    cells = read(archive / "cells.json")
    expected = {
        (t["id"], s, a)
        for t in targets
        for s in manifest["seeds"]
        for a in manifest["arms"]
    }
    if (
        len(cells) != len(expected)
        or {(c["target"], c["seed"], c["arm"]) for c in cells} != expected
    ):
        raise ValueError("incomplete or duplicate cells")
    rates = {t["id"]: t["target_rates"] for t in targets}
    for cell in cells:
        target = rates[cell["target"]]
        control = Control(
            cell["arm"], cell["seed"], manifest["budget"], target, manifest["scale"]
        )
        trials = cell["trials"]
        if len(trials) != manifest["budget"] or [t["slot"] for t in trials] != list(
            range(1, manifest["budget"] + 1)
        ):
            raise ValueError("incomplete trajectory")
        offset = 0
        for decision in cell["decisions"]:
            if control.ask() != decision:
                raise ValueError("proposal, screening or parent visibility differs")
            count = len(decision["proposals"])
            batch = trials[offset : offset + count]
            for trial in batch:
                if trial["status"] == "MEASURED":
                    check_trial(archive, trial, manifest)
                    check_loss(trial, target, manifest["scale"])
                elif trial["status"] != "FILTERED" or any(
                    trial[k] is not None for k in ("valid", "rates", "loss")
                ):
                    raise ValueError("filtered candidate carries measurement")
            control.tell(batch)
            offset += count
        if offset != manifest["budget"]:
            raise ValueError("missing decisions")
    summary = describe(cells, manifest)
    summary["witness_attempts"] = len(witnesses)
    summary["valid_witnesses"] = sum(t["valid"] for t in witnesses)
    summary["target_pairwise_nrmse"] = [
        {
            "left": a["id"],
            "right": b["id"],
            "distance": math.sqrt(
                sum(
                    ((x - y) / manifest["scale"]) ** 2
                    for x, y in zip(a["target_rates"], b["target_rates"], strict=True)
                )
                / 8
            ),
        }
        for i, a in enumerate(targets)
        for b in targets[i + 1 :]
    ]
    summary["unique_evaluation_records_including_construction"] = len(
        {
            t["cache_id"]
            for t in witnesses + [t for c in cells for t in c["trials"]]
            if t.get("cache_id")
        }
    )
    if (archive / "summary.json").exists() and read(
        archive / "summary.json"
    ) != summary:
        raise ValueError("summary differs")
    return summary
