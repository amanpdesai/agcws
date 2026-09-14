import runpy

import pytest

from agcws.nodes.bit_activity import CONTRACT


def test_bit_calibration_recomputes_scale_and_keeps_failures():
    calibration = runpy.run_path("analysis/bit_bank.py")["calibration"]
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
    select = runpy.run_path("analysis/bit_requalification.py")["fixed_cases"]
    rows = [{"id": f"calibration-{i:02}", "program": {"test": i}, "measurement": {"valid": False}}
            for i in range(64)]
    rows += [{"id": f"{split}-{i}", "program": {"test": i}}
             for split in ("development", "confirmation") for i in range(9)]
    bundle = {"out/aes-runtime-replay-v5/replay/complete.json": {"data": {"results": rows}}}
    cases = select(bundle, "aes")
    assert len(cases) == 82
    assert sum(c["id"].startswith("calibration-") for c in cases) == 64
    rows.pop()
    with pytest.raises(ValueError, match="64 calibration"):
        select(bundle, "aes")
