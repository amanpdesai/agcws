import pytest

from analysis.baseline_panel_v1_diagnostics import flat_error


def test_constant_vector_is_not_temporally_demanding():
    assert flat_error([12.0] * 8, 10) == 0


def test_best_constant_uses_centered_rms_not_range():
    assert flat_error([0.0, 20.0] * 4, 10) == pytest.approx(1.0)


def test_flat_error_is_offset_invariant():
    assert flat_error([0.0, 20.0] * 4, 10) == flat_error([100.0, 120.0] * 4, 10)
