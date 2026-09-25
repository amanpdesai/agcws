import pytest

from agcws.reporting.metrics import error, max_bin_error, success, summarize


def test_one_bad_bin_cannot_hide_in_rmse():
    rates, target = [.12]+[0]*7, [0]*8
    trial = {"slot": 1, "valid": True, "loss": error(rates, target, 1),
             "max_bin_error": max_bin_error(rates, target, 1)}
    assert success(trial, .05)
    assert not success(trial, .05, "max-bin")
    with pytest.raises(ValueError, match="tolerance hit"):
        summarize([trial], 128, .05, stop_on_success=True, success_metric="max-bin")
    second = {"slot": 2, "valid": True, "loss": .05, "max_bin_error": .05}
    result = summarize([trial, second], 128, .05, stop_on_success=True, success_metric="max-bin")
    assert result["evaluations_to_target"] == 2
    assert result["charged_slots"] == 2
    assert result["auc_metric"] == "nrmse"


def test_missing_or_nonfinite_bin_metric_fails_closed():
    with pytest.raises(KeyError):
        success({"valid": True, "loss": 0}, .05, "max-bin")
    with pytest.raises(ValueError):
        max_bin_error([float("nan")]*8, [0]*8, 1)
    assert not success({"valid": False}, .05, "max-bin")
