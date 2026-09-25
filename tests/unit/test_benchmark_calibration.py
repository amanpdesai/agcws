import statistics

import pytest

from agcws.core.storage import read, write
from agcws.studies.calibration import DOMAINS, plan, report
from agcws.studies.targets import mean_matched_requests


def test_plan_is_cpu_only_and_has_no_early_stopping(tmp_path):
    binary = tmp_path / "simulator"
    binary.touch()
    out = tmp_path / "configs"
    assert plan(out, "test-image", binary)["slots_per_design"] == 64
    for domain in DOMAINS:
        spec = read(out / f"{domain}.json")
        assert spec["policies"] == ["random"] and spec["stop_on_success"] is False
        assert spec["seeds"] == [7200, 7201]
        assert spec["targets"] == {"calibration_only": [0.0]*8}


@pytest.mark.parametrize("split", ["development", "confirmation"])
def test_mean_matched_requests_preserve_resource_mean(split):
    requests = mean_matched_requests(2, 100, 15, split=split)
    assert len(requests) == 9 and sum(r["control"] for r in requests) == 1
    for request in requests:
        assert statistics.mean(request["rates"]) == pytest.approx(15)
        assert all(2 <= v <= 100 for v in request["rates"])
        assert not request["qualified"]
    with pytest.raises(ValueError):
        mean_matched_requests(2, 100, 101, split=split)


def calibration_fixture(tmp_path, valid_count):
    spec = {"domain": "aes-temporal", "seeds": [7200, 7201], "policies": ["random"],
            "budget": 32, "stop_on_success": False, "targets": {"calibration_only": [0.0]*8}}
    write(tmp_path / "manifest.json", {"spec": spec, "measurement_fingerprint": "test"})
    write(tmp_path / "complete.json", {"slots": 64})
    write(tmp_path / "panel/trials.json", [
        {"valid": i < valid_count, "rates": list(range(8)) if i < valid_count else None,
         "stage": None if i < valid_count else "USEFUL_WORK"} for i in range(64)])


def test_report_preserves_rejections_and_inclusive_quantiles(tmp_path):
    calibration_fixture(tmp_path, 40)
    result = report(tmp_path)
    assert result["proposals"] == 64 and result["valid"] == 40
    assert result["failure_stages"] == {"USEFUL_WORK": 24}
    assert result["low"] == 0 and result["high"] == 7
    assert result["median_window_mean"] == 3.5
    assert not result["target_qualified"]


def test_insufficient_calibration_never_produces_endpoints(tmp_path):
    calibration_fixture(tmp_path, 31)
    result = report(tmp_path)
    assert result["status"] == "insufficient_valid_calibration"
    assert "low" not in result and "scale" not in result
