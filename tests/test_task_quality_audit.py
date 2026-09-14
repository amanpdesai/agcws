import json
import runpy

import pytest


def test_single_bin_error_and_tolerance_ball_overlap():
    functions = runpy.run_path("analysis/task_quality_audit.py")
    flat = [0]*8
    spike = [0]*7 + [1]
    assert functions["rmse"](flat, spike, 1) == pytest.approx(1/8**.5)
    assert functions["shape"]([.3]*8, 1)["constant_floor"] == 0
    pairs = functions["geometry"]([{"key": "a", "rates": flat}, {"key": "b", "rates": [.15]*8}], 1)
    assert pairs[0]["unconstrained_tolerance_balls_overlap"]
    assert functions["rmse"](flat, [.15]*8, 1) > .1


def test_geometry_rejects_bad_dimensions_and_nan():
    rmse = runpy.run_path("analysis/task_quality_audit.py")["rmse"]
    with pytest.raises(ValueError):
        rmse([0]*7, [0]*8, 1)
    with pytest.raises(ValueError):
        rmse([float("nan")]*8, [0]*8, 1)


def test_captured_inputs_reproduce_without_original_files_and_detect_tampering(tmp_path):
    inputs_class = runpy.run_path("analysis/task_quality_audit.py")["Inputs"]
    path = tmp_path / "input.json"
    path.write_text(json.dumps({"value": [1, 2]}))
    original = inputs_class(tmp_path)
    expected = original.read(path)
    path.unlink()
    assert inputs_class(tmp_path, original.records).read(path) == expected
    original.records["input.json"]["data"]["value"][0] = 99
    with pytest.raises(ValueError, match="hash mismatch"):
        inputs_class(tmp_path, original.records)
