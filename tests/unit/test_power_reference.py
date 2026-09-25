import pytest

from agcws.reporting.power_reference import tracking


def test_identical_trace_matches_and_uses_own_durations():
    result = tracking([1, 2] * 4, [1, 2] * 4, [1, 3] * 4)
    assert result["nrmse"] == 0
    assert result["scale_w"] == 1.75
    assert result["candidate_energy_j"] == 28


def test_equal_energy_does_not_hide_temporal_mismatch():
    result = tracking([2, 0] * 4, [0, 2] * 4, [1] * 8)
    assert result["candidate_energy_j"] == result["reference_energy_j"]
    assert result["nrmse"] == 2
    assert result["max_bin_error"] == 2


def test_candidate_amplitude_is_not_normalized_away():
    result = tracking([2] * 8, [1] * 8, [1] * 8)
    assert result["nrmse"] == 1
    assert result["scale_w"] == 1
    assert result["constant_reference"]
    assert result["error_over_constant_floor"] is None


def test_small_total_error_does_not_hide_missing_modulation():
    result = tracking([100] * 8, [99, 101] * 4, [1] * 8)
    assert result["nrmse"] == .01
    assert result["best_constant_nrmse"] == .01
    assert result["error_over_constant_floor"] == 1
    assert result["reference_modulation_fraction"] == .02


@pytest.mark.parametrize("candidate,reference,durations", [
    ([1] * 7, [1] * 8, [1] * 8),
    ([1] * 8, [0] * 8, [1] * 8),
    ([float("nan")] * 8, [1] * 8, [1] * 8),
    ([1] * 8, [-1] * 8, [1] * 8),
    ([1] * 8, [1] * 8, [0] * 8),
])
def test_invalid_measurements_are_not_scored(candidate, reference, durations):
    with pytest.raises(ValueError):
        tracking(candidate, reference, durations)
