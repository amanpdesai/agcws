import itertools

import pytest

from analysis.ibex_expressiveness import audit_cell, describe


def panel():
    manifest = {
        "targets": {"a": {}, "b": {}},
        "seeds": [1, 2],
        "policies": ["random"],
        "scale": 10,
        "budget": 2,
    }
    cells = []
    for target, seed, policy in itertools.product(
        manifest["targets"], manifest["seeds"], manifest["policies"]
    ):
        cells.append(
            (
                {
                    "target": target,
                    "seed": seed,
                    "policy": policy,
                    "auc": 0.5,
                    "final_loss": 0.1,
                    "solved": False,
                    "evaluations_to_target": 2,
                    "est_cost_usd": 0,
                    "unknown_usage_batches": 0,
                },
                [
                    {"slot": 1, "valid": False, "stage": "SCHEMA"},
                    {"slot": 2, "valid": True, "rates": [1] * 8},
                ],
            )
        )
    return manifest, cells


def test_descriptive_panel_retains_failures_and_censoring():
    manifest, cells = panel()
    result = describe(manifest, cells)["policies"]["random"]
    assert result["mean_auc"] == 0.5
    assert result["validity"] == {"SCHEMA": 4, "VALID": 4}
    assert result["solved_cells"] == 0 and result["mean_censored_proposals"] == 2
    assert result["grid_profiles"] == 1


def test_incomplete_or_duplicate_panel_cannot_be_reported_complete():
    manifest, cells = panel()
    for rows in (cells[:-1], cells + [cells[0]]):
        with pytest.raises(ValueError):
            describe(manifest, rows)


def test_cell_audit_rejects_fabricated_auc():
    manifest = {
        "targets": {"t": {"rates": [0] * 8}},
        "scale": 1,
        "budget": 2,
        "tolerance": 0.1,
    }
    rows = [
        {
            "slot": i,
            "valid": False,
            "loss": None,
            "rates": None,
            "best_loss": 1,
            "est_cost_usd": 0,
        }
        for i in [1, 2]
    ]
    summary = {
        "target": "t",
        "auc": 1,
        "solved": False,
        "evaluations_to_target": 2,
        "right_censored": True,
        "est_cost_usd": 0,
    }
    audit_cell(manifest, summary, rows, {})
    summary["auc"] = 0
    with pytest.raises(ValueError, match="AUC mismatch"):
        audit_cell(manifest, summary, rows, {})
