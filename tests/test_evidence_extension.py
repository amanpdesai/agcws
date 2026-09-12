import hashlib
import json
import math
from pathlib import Path

import pytest

from analysis.accounting_math import prefix
from analysis.evidence_extension import costs, coverage


def calibration():
    return {"p_min": 10, "p_max": 110, "epsilon_scalar": 0.02, "useful_work_floor": 38}


def row(index, activity, valid=True, work=38):
    return {"index": index, "activity": activity, "valid": valid, "useful_work": work}


def test_coverage_is_not_occupancy_and_does_not_clip():
    result = coverage([row(0, 10), row(1, 110), row(2, 15), row(3, 120)], calibration())
    assert result["coverage"] == 0.1
    assert result["occupancy_secondary"] == 0.2
    assert result["out_of_envelope_indices"] == [3]
    assert result["hit_indices"][0] == [2]


def test_coverage_rejects_subfloor_valid_and_excludes_invalid():
    with pytest.raises(ValueError, match="sub-floor"):
        coverage([row(0, 15, work=37)], calibration())
    assert coverage([row(0, 15, valid=False, work=0)], calibration())["coverage"] == 0


@pytest.mark.parametrize("field,value", [("p_max", 10), ("p_min", math.nan), ("epsilon_scalar", 0)])
def test_bad_envelope_refused(field, value):
    c = calibration()
    c[field] = value
    with pytest.raises(ValueError):
        coverage([], c)


def test_nonfinite_activity_refused():
    with pytest.raises(ValueError, match="nonfinite"):
        coverage([row(0, math.inf)], calibration())


def test_cost_includes_unknown_and_unsolved_spend():
    requests = [
        {"known": 2, "reserved": 0, "duration_s": 1},
        {"known": 0, "reserved": 3, "duration_s": 4},
    ]
    result = costs(requests, solves=1, cells=2)
    assert result["known_usd_per_run"] == 1
    assert result["known_usd_per_solved_cell"] == 2
    assert result["liability_usd_per_solved_cell"] == 5
    assert result["compute_cost_usd"] is None
    assert costs(requests, solves=0, cells=2)["known_usd_per_solved_cell"] is None
    assert costs([], solves=1, cells=2)["known_usd_per_solved_cell"] == 0


def test_prefix_censors_unsolved_and_preserves_first_valid_above_one():
    rows = [
        {"slot": 1, "valid": False, "loss": None},
        {"slot": 2, "valid": True, "loss": 2.0},
        {"slot": 3, "valid": True, "loss": 0.05},
    ]
    short = prefix(rows, 2, 0.1)
    assert short["auc"] == 1.5 and short["right_censored"]
    assert short["evaluations_to_target"] == 2
    long = prefix(rows, 3, 0.1)
    assert long["solved"] and long["evaluations_to_target"] == 3


def test_prefix_refuses_missing_slot_or_scored_failure():
    with pytest.raises(ValueError):
        prefix([{"slot": 1, "valid": True, "loss": 1}], 2, 0.1)
    with pytest.raises(ValueError):
        prefix([{"slot": i, "valid": False, "loss": 0} for i in (1, 2)], 2, 0.1)


def test_frozen_readiness_and_secondary_bundle_hashes():
    repo = Path(__file__).resolve().parents[1]
    root = repo / "results/evidence_extension_v1"
    frozen = json.loads((root / "freeze.json").read_text())
    for name, expected in frozen["files_sha256"].items():
        assert hashlib.sha256((repo / name).read_bytes()).hexdigest() == expected, name
    recorded = {
        name for name in frozen["files_sha256"] if name.startswith("results/evidence_extension_v1/")
    }
    actual = {
        str(p.relative_to(repo)) for p in root.rglob("*") if p.is_file() and p.name != "freeze.json"
    }
    assert recorded == actual
    readiness = json.loads((root / "control_readiness.json").read_text())
    assert readiness["historical_current_equal"]
    assert readiness["fixture_cells"] == 36 and readiness["synthetic_slots"] == 768
    assert readiness["compiler_state_examples"] == 102
    for name, expected in readiness["source_sha256"].items():
        assert hashlib.sha256((repo / name).read_bytes()).hexdigest() == expected, name
    assert len(list((root / "workloads").glob("*.json"))) == 15
