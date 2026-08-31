from agcws.experiments.calibration import choose_scalar_epsilon


def test_scalar_calibration_rule_matches_preregistered_thresholds():
    assert choose_scalar_epsilon(0.1) == 0.05
    assert choose_scalar_epsilon(0.6) == 0.05
    assert choose_scalar_epsilon(0.6001) == 0.02
