import json

import pytest

from agcws.reporting import benchmark_audit


def test_single_bin_error_and_tolerance_ball_overlap():
    functions = vars(benchmark_audit)
    flat = [0]*8
    spike = [0]*7 + [1]
    assert functions["rmse"](flat, spike, 1) == pytest.approx(1/8**.5)
    assert functions["shape"]([.3]*8, 1)["constant_floor"] == 0
    pairs = functions["geometry"]([{"key": "a", "rates": flat}, {"key": "b", "rates": [.15]*8}], 1)
    assert pairs[0]["unconstrained_tolerance_balls_overlap"]
    assert functions["rmse"](flat, [.15]*8, 1) > .1


def test_geometry_rejects_bad_dimensions_and_nan():
    rmse = vars(benchmark_audit)["rmse"]
    with pytest.raises(ValueError):
        rmse([0]*7, [0]*8, 1)
    with pytest.raises(ValueError):
        rmse([float("nan")]*8, [0]*8, 1)


def test_captured_inputs_reproduce_without_original_files_and_detect_tampering(tmp_path):
    inputs_class = vars(benchmark_audit)["Inputs"]
    path = tmp_path / "input.json"
    path.write_text(json.dumps({"value": [1, 2]}))
    original = inputs_class(tmp_path)
    expected = original.read(path)
    path.unlink()
    assert inputs_class(tmp_path, original.records).read(path) == expected
    original.records["input.json"]["data"]["value"][0] = 99
    with pytest.raises(ValueError, match="hash mismatch"):
        inputs_class(tmp_path, original.records)


def test_calibration_keeps_failures_and_uses_inclusive_quantiles():
    check = vars(benchmark_audit)["calibration_check"]
    rows = [{"id": f"calibration-{i:02}", "measurement": {
        "valid": i < 63, "stage": "USEFUL_WORK" if i == 63 else None,
        "profile": {"window_rates": [float(i)]*8}}} for i in range(64)]
    expected = {"low": 3., "high": 59., "scale": 56., "median_window_mean": 31.,
                "valid": 63, "failure_stages": {"USEFUL_WORK": 1}}
    assert check(rows, expected)["valid"] == 63
    with pytest.raises(ValueError, match="64"):
        check(rows[:-1], expected)
    with pytest.raises(ValueError, match="differs"):
        check(rows, {**expected, "scale": 57.})


def test_difficulty_rejects_scored_invalid_trials():
    trials = [{"slot": i, "valid": True, "loss": 0., "rates": [0.] * 8}
              for i in range(1, 17)]
    assert benchmark_audit.verify_trials(trials, [0.] * 8, 1.) == 16
    trials[0]["valid"] = False
    with pytest.raises(ValueError, match="invalid trial has a score"):
        benchmark_audit.verify_trials(trials, [0.] * 8, 1.)


def test_difficulty_rejects_fabricated_loss():
    with pytest.raises(ValueError, match="loss differs"):
        benchmark_audit.verify_trials(
            [{"valid": True, "loss": 0., "rates": [1.] * 8}], [0.] * 8, 1.)
