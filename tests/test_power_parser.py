import pytest

from agcws.nodes.power import parse_opensta_power_report
from agcws.goals import ScalarGoal, TemporalGoal
from agcws.goals.loss import loss
from agcws.nodes.power import PowerProfile


def test_parse_opensta_power_report():
    profile = parse_opensta_power_report("Total Power = 1.25e-03\n")
    assert profile.valid
    assert profile.mean_power == pytest.approx(0.00125)
    assert profile.fidelity == "synthesis"


def test_power_parser_rejects_missing_total():
    with pytest.raises(ValueError, match="Total Power"):
        parse_opensta_power_report("Switching Power = 1.0e-03\n")


def test_parse_real_opensta_summary_table():
    report = "Total                  1.99e-02   1.26e-03   1.36e-07   2.12e-02 100.0%\n"
    profile = parse_opensta_power_report(report)
    assert profile.mean_power == pytest.approx(2.12e-2)


def test_goal_losses_are_deterministic():
    profile = PowerProfile(5.0, 5.0, windowed=[1.0, 2.0, 1.0], valid=True)
    assert loss(profile, ScalarGoal(0.5), p_min=1.0, p_max=9.0) == pytest.approx(0.0)
    assert loss(profile, TemporalGoal(3, [0.5, 1.0, 0.5])) == pytest.approx(0.0)
