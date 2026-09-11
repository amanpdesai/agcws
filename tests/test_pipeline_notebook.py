import copy

import pytest

from agcws.pipeline.ibex.notebook import assess, changes, notebook


def records():
    before = {
        "slot": 2,
        "valid": True,
        "rates": [100] * 8,
        "canonical_program": {"registers": [0, 1]},
    }
    after = {
        "slot": 3,
        "valid": True,
        "rates": [110] * 8,
        "canonical_program": {"registers": [0, 0]},
        "prediction": {"reference_slot": 2, "window_directions": [-1] * 8},
    }
    return before, after


def test_failed_prediction_is_retained_and_actual_edit_identified():
    before, after = records()
    result = assess(after, [before], 100)
    assert result["scorable"] and result["matched_bins"] == 0
    assert result["actual_changes"] == [{"path": ["registers", 1], "before": 1, "after": 0}]
    assert after["valid"]


def test_missing_or_future_reference_does_not_change_workload_validity():
    before, after = records()
    assert not assess(after, [], 100)["scorable"]
    before["slot"] = 4
    after["prediction"]["reference_slot"] = 4
    assert not assess(after, [before], 100)["scorable"]
    assert after["valid"]


def test_neutral_band_and_invalid_candidate_are_explicit():
    before, after = records()
    after["rates"] = [101] * 8
    assert assess(after, [before], 100)["observed_directions"] == [0] * 8
    after["valid"] = False
    assert assess(after, [before], 100)["reason"] == "candidate has no valid measurement"


def test_structural_edits_are_not_misrepresented_as_single_numeric_edits():
    assert changes({"body": [1]}, {"body": [1, 2]}) == [
        {"path": ["body"], "before": [1], "after": [1, 2]}
    ]
    before, after = records()
    later = copy.deepcopy(after)
    later["slot"] = 4
    before["proposal_mode"] = "initial"
    assert [x["slot"] for x in notebook([before, after, later], 100, limit=1)] == [4]
    with pytest.raises(ValueError):
        notebook([], 1, limit=0)
