"""Independent evidence checks and complete-panel paired inference."""

import itertools
import math
import random
import statistics

from analysis.ibex_depth_v1 import check_prefix_arithmetic, check_trial, value
from analysis.temporal_scaling_v1 import check_loss
from experiments.baseline_panel_v1.policies import witness_program
from experiments.ibex_depth_v1.model import cost
from experiments.ibex_depth_v1.storage import read
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.nonflat_temporal_v1.study import cpu_candidates, identity, selected


def check_witnesses(archive, m, trials):
    if [t["slot"] for t in trials] != list(range(1, m["construction_count"] + 1)):
        raise ValueError("missing construction attempts")
    rng = random.Random(m["construction_seed"])
    for t in trials:
        if t["program"] != witness_program("scheduled-four-phase", rng, t["slot"]):
            raise ValueError("construction program differs")
        check_trial(archive, t, m)
        check_loss(t, [0.0] * 8, m["scale"])


def check_cell(archive, m, cell, budget):
    ident = cell["cell"]
    targets = {t["id"]: t["rates"] for t in read(archive / "targets.json")}
    target = targets[ident["target"]]
    trials = cell["trials"]
    if len(trials) != budget or [t["slot"] for t in trials] != list(
        range(1, budget + 1)
    ):
        raise ValueError("incomplete trajectory")
    rng = random.Random(ident["seed"])
    section = "smoke" if budget == m["smoke_budget"] else "panel"
    directory = f"{section}/{ident['target']}/{ident['seed']}/{ident['arm']}/batches"
    for offset in range(0, budget, 2):
        batch = trials[offset : offset + 2]
        model_batch = ident["arm"] == "pro-4096" and offset > 0
        saved = value(archive, f"{directory}/{offset + 1:03}/input.json")
        if model_batch:
            contents = payload(
                trials[:offset],
                {"profile": target, "scale": m["scale"], "tolerance": m["tolerance"]},
                2,
                True,
            )
            if saved["payload"] != contents or saved["cpu_candidates"] is not None:
                raise ValueError("history/context or witness isolation differs")
            response = value(archive, f"{directory}/{offset + 1:03}/response.json")
            if response["identity"] != saved["identity"]:
                raise ValueError("response identity differs")
            if not response["usage_unknown"] and not math.isclose(
                response["estimated_usd"],
                cost(ident["arm"], response["tokens_in"], response["tokens_out"]),
            ):
                raise ValueError("cost differs")
            proposals = decode(response["raw_text"], 2, True)
        else:
            candidates = cpu_candidates(rng, offset)
            if saved["cpu_candidates"] != candidates or saved["payload"] is not None:
                raise ValueError("baseline regeneration differs")
            import json

            proposals = decode(
                json.dumps({"hypothesis": "CPU proposal", "candidates": candidates}), 2
            )
        if proposals != value(archive, f"{directory}/{offset + 1:03}/decoded.json"):
            raise ValueError("decode differs")
        for proposal, trial in zip(proposals["slots"], batch, strict=True):
            if proposal["submitted"] != trial["program"]:
                raise ValueError("submitted program differs")
            check_trial(archive, trial, m)
            check_loss(trial, target, m["scale"])
    for summary in cell["prefixes"].values():
        check_prefix_arithmetic(trials, summary, m["tolerance"])


def inference(differences):
    if len(differences) != 6 or any(not math.isfinite(x) for x in differences):
        raise ValueError("six finite seed differences required")
    mean = statistics.mean(differences)
    null = [
        abs(statistics.mean(s * x for s, x in zip(signs, differences, strict=True)))
        for signs in itertools.product((-1, 1), repeat=6)
    ]
    p = sum(v >= abs(mean) - 1e-12 for v in null) / len(null)
    rng = random.Random(1300)
    boot = sorted(statistics.mean(rng.choices(differences, k=6)) for _ in range(10000))
    return {
        "mean_difference": mean,
        "seed_differences": differences,
        "two_sided_exact_sign_flip_p": p,
        "seed_bootstrap_95_percentile": [boot[249], boot[9749]],
        "scope": "six seed units; conditional on this target bank, not 18 independent replicates",
    }


def audit(archive):
    m = identity(archive)
    witnesses = read(archive / "witnesses.json")
    check_witnesses(archive, m, witnesses)
    if selected(witnesses, m) != read(archive / "targets.json"):
        raise ValueError("selection differs")
    expected = read(archive / "search_manifest.json")["cells"]
    cells = []
    for c in expected:
        result = read(
            archive
            / "panel"
            / c["target"]
            / str(c["seed"])
            / c["arm"]
            / "complete.json"
        )
        if result["cell"] != c:
            raise ValueError("cell identity differs")
        check_cell(archive, m, result, m["budget"])
        cells.append(result)
    lookup = {
        (c["cell"]["target"], c["cell"]["seed"], c["cell"]["arm"]): c for c in cells
    }
    targets = [t["id"] for t in read(archive / "targets.json")]
    differences = [
        statistics.mean(
            lookup[t, s, "pro-4096"]["prefixes"]["128"]["auc"]
            - lookup[t, s, "phase-random"]["prefixes"]["128"]["auc"]
            for t in targets
        )
        for s in m["seeds"]
    ]
    arms = {}
    for arm in m["arms"]:
        group = [c for c in cells if c["cell"]["arm"] == arm]
        summaries = [c["prefixes"]["128"] for c in group]
        stages = {}
        for t in [t for c in group for t in c["trials"]]:
            stage = "VALID" if t["valid"] else t["stage"]
            stages[stage] = stages.get(stage, 0) + 1
        arms[arm] = {
            "mean_auc": statistics.mean(s["auc"] for s in summaries),
            "solves": sum(s["solved"] for s in summaries),
            "mean_censored_slots": statistics.mean(
                s["evaluations_to_target"] for s in summaries
            ),
            "validity": stages,
        }
    equal_valid = []
    for t in targets:
        for s in m["seeds"]:
            valid = {
                a: [r for r in lookup[t, s, a]["trials"] if r["valid"]]
                for a in m["arms"]
            }
            n = min(map(len, valid.values()))
            equal_valid.append(
                {
                    "target": t,
                    "seed": s,
                    "common_valid_count": n,
                    "best_errors": {
                        a: min(r["loss"] for r in rows[:n]) if n else None
                        for a, rows in valid.items()
                    },
                }
            )
    return {
        "complete": True,
        "cells": len(cells),
        "slots": len(cells) * m["budget"],
        "primary": inference(differences),
        "arms": arms,
        "equal_valid_secondary": equal_valid,
        "cell_metrics": [{"cell": c["cell"], "prefixes": c["prefixes"]} for c in cells],
    }
