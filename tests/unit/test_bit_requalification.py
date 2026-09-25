import pytest

from agcws.evaluation.activity.known_bits import CONTRACT
from agcws.evidence.bit_bank import calibration, fixed_cases


def test_bit_calibration_recomputes_scale_and_keeps_failures():
    rows = [{"id": f"calibration-{i:02}", "measurement": {
        "valid": i < 63, "stage": "USEFUL_WORK" if i == 63 else None,
        "profile": {"activity_contract": CONTRACT, "window_rates": [float(i)]*8}}}
        for i in range(64)]
    result = calibration(rows)
    assert result["scale"] == 56
    assert result["valid"] == 63
    assert result["failure_stages"] == {"USEFUL_WORK": 1}
    assert result["status"] == "calibrated"
    rows[0]["measurement"]["profile"]["activity_contract"] = "old-event-counter"
    with pytest.raises(ValueError, match="contract"):
        calibration(rows)


def test_fixed_program_selection_preserves_invalid_calibration_inputs():
    rows = [{"id": f"calibration-{i:02}", "program": {"test": i}, "measurement": {"valid": False}}
            for i in range(64)]
    rows += [{"id": f"{split}-{i}", "program": {"test": i}}
             for split in ("development", "confirmation") for i in range(9)]
    cases = fixed_cases(rows, rows)
    assert len(cases) == 82
    assert sum(c["id"].startswith("calibration-") for c in cases) == 64
    rows.pop()
    with pytest.raises(ValueError, match="64 calibration"):
        fixed_cases(rows, rows)
