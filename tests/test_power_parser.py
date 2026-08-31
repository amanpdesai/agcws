import pytest

from agcws.nodes.power import parse_opensta_power_report


def test_parse_opensta_power_report():
    profile = parse_opensta_power_report("Total Power = 1.25e-03\n")
    assert profile.valid
    assert profile.mean_power == pytest.approx(0.00125)
    assert profile.fidelity == "synthesis"


def test_power_parser_rejects_missing_total():
    with pytest.raises(ValueError, match="Total Power"):
        parse_opensta_power_report("Switching Power = 1.0e-03\n")
