import itertools
import json
import shutil
from pathlib import Path

import pytest

from analysis.ibex_temporal_v4 import (
    check_execution,
    check_prerequisites,
    describe_panel,
)
from experiments.ibex_temporal_v3.feedback import CLASSES


def feedback():
    return {
        "begin_tick": 10,
        "end_tick": 400010,
        "cycles_per_bin": 25000,
        "retired_per_bin": [1] * 8,
        "cycles_without_retirement": [24999] * 8,
        "retired_classes": [{k: int(k == "alu") for k in CLASSES} for _ in range(8)],
    }


def test_execution_audit_checks_divide_counts_and_windows():
    data = {
        "begin_tick": 10,
        "end_tick": 400010,
        "bins": [
            {
                "retired_by_phase": {"body": 1},
                "divide_zero_divisor": 0,
                "divide_nonzero_divisor": 0,
            }
            for _ in range(8)
        ],
    }
    check_execution(data, feedback())
    data["bins"][0]["divide_zero_divisor"] = 1
    with pytest.raises(ValueError, match="divide"):
        check_execution(data, feedback())
    data["end_tick"] = 400012
    with pytest.raises(ValueError, match="window"):
        check_execution(data, feedback())


def test_descriptive_predictions_keep_missing_denominator_and_remove_union_coverage():
    manifest = {
        "targets": {"t": {}},
        "seeds": [1, 2],
        "policies": ["random", "agent"],
        "budget": 3,
        "scale": 100,
    }
    cells = []
    for seed, policy in itertools.product(manifest["seeds"], manifest["policies"]):
        summary = {
            "target": "t",
            "seed": seed,
            "policy": policy,
            "auc": 1,
            "final_loss": 0.2,
            "solved": False,
            "evaluations_to_target": 3,
            "est_cost_usd": 0,
            "unknown_usage_batches": 0,
        }
        assessment = (
            {"scorable": False, "reason": "missing"}
            if policy == "random"
            else {
                "scorable": True,
                "matched_bins": 4,
                "observed_directions": [0] * 4 + [1] * 4,
                "all_directions_supported": False,
                "actual_changes": [],
            }
        )
        trials = [
            {
                "slot": i,
                "valid": True,
                "stage": None,
                "rates": [1] * 8,
                "feedback": feedback(),
                "tokens_in": 0,
                "tokens_out": 0,
                "prediction_assessment": assessment,
            }
            for i in (1, 2, 3)
        ]
        cells.append((summary, trials))
    result = describe_panel(manifest, cells)
    assert result["policies"]["random"]["predictions"]["generated_slots"] == 2
    assert result["policies"]["random"]["predictions"]["scorable_bins"] == 0
    assert result["policies"]["agent"]["predictions"]["matched_bins"] == 8
    assert result["policies"]["agent"]["predictions"]["scorable_bins"] == 16
    assert "grid_profiles" not in result["policies"]["agent"]
    with pytest.raises(ValueError, match="incomplete"):
        describe_panel(manifest, cells[:-1])


def test_frozen_readiness_prerequisites_are_reproducible_and_tamper_evident(tmp_path):
    manifest = json.loads(
        Path("results/ibex_temporal_v4_development/manifest.json").read_text()
    )
    for name in (
        "ibex_temporal_v4_gate",
        "ibex_temporal_v4_gate_tiny",
        "ibex_temporal_v4_prediction_gate",
    ):
        shutil.copytree(Path("results") / name, tmp_path / "prerequisites" / name)
    check_prerequisites(tmp_path, manifest)
    path = (
        tmp_path
        / "prerequisites/ibex_temporal_v4_prediction_gate/inputs/prediction.json"
    )
    path.write_text("{}\n")
    with pytest.raises(ValueError, match="input mismatch"):
        check_prerequisites(tmp_path, manifest)
