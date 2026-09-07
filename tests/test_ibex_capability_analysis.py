import itertools

import pytest

from analysis.ibex_capability_v1 import describe
from experiments.ibex_capability_v1.study import ARMS


def fixture_records(gains):
    contexts = {
        f"t{t}-s{s}": {"target": t, "seed": s}
        for t, s in itertools.product(range(4), range(3))
    }
    declared = [{"context": c, "arm": a} for c, a in itertools.product(contexts, ARMS)]
    records = []
    for cell in declared:
        gain = gains[cell["arm"]]
        r = {
            "cell": cell,
            "summary": {
                "gain": gain,
                "after_error": 0.2 - gain,
                "improved": gain > 0,
                "already_solved": False,
                "newly_solved": False,
            },
            "trials": [
                {
                    "valid": True,
                    "stage": None,
                    "prediction_assessment": {"scorable": False, "reason": "missing"},
                }
                for _ in range(2)
            ],
        }
        response = {
            "tokens_in": 0,
            "tokens_out": 0,
            "est_cost_usd": 0,
            "usage_unknown": False,
        }
        records.append((r, response))
    return {"contexts": contexts, "cells": declared}, records


def test_factorial_primary_contrasts_screen_and_missing_cells():
    manifest, records = fixture_records(
        dict(zip(ARMS, (0.01, 0.02, 0.03, 0.05, 0.005, 0.005)))
    )
    output = describe(manifest, records)
    assert output["arms"]["flash-512"]["mean_gain"] == 0.01
    assert output["arms"]["pro-4096"]["requested_slots"] == 24
    assert output["paired_gain_contrasts"]["interaction"] == pytest.approx(0.01)
    assert output["screened_candidate"] == "pro-4096"
    assert output["arms"]["pro-4096"]["predictions"]["scorable"] == 0
    with pytest.raises(ValueError, match="incomplete"):
        describe(manifest, records[:-1])


def test_unknown_usage_disqualifies_screen_without_dropping_primary():
    manifest, records = fixture_records(
        {a: 0.1 if a == "pro-4096" else 0 for a in ARMS}
    )
    for record, response in records:
        response["usage_unknown"] = record["cell"]["arm"] == "pro-4096"
    result = describe(manifest, records)
    assert result["screened_candidate"] is None
    assert result["arms"]["pro-4096"]["mean_gain"] == pytest.approx(0.1)
