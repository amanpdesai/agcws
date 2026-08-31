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


def test_parse_real_opensta_summary_table():
    report = "Total                  1.99e-02   1.26e-03   1.36e-07   2.12e-02 100.0%\n"
    profile = parse_opensta_power_report(report)
    assert profile.mean_power == pytest.approx(2.12e-2)
