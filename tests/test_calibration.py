import pytest

from agcws.experiments.calibration import calibration_record, choose_scalar_epsilon


def test_epsilon_rule_has_expected_boundaries():
    assert choose_scalar_epsilon(0.0) == 0.10
    assert choose_scalar_epsilon(0.6) == 0.05
    assert choose_scalar_epsilon(0.61) == 0.02


def test_calibration_record_computes_envelope_and_floor():
    result = calibration_record([
        {"mean_power": 2.0, "useful_work": 16, "valid": True},
        {"mean_power": 3.0, "useful_work": 32, "valid": True},
        {"mean_power": 99.0, "useful_work": 1, "valid": False},
    ])
    assert result["p_min"] == 2.0 and result["p_max"] == 3.0
    assert result["useful_work_floor"] == 17
    assert result["status"].startswith("provisional")


def test_epsilon_rejects_invalid_fraction():
    with pytest.raises(ValueError):
        choose_scalar_epsilon(1.1)
