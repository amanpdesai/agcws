import runpy
import statistics

import pytest

from agcws.pipeline.storage import read

generate = runpy.run_path("scripts/prepare_target_bank.py")["fixed_work_requests"]


@pytest.mark.parametrize("domain", ["aes-temporal", "dma-temporal"])
def test_fixed_work_requests_preserve_mean_and_strengthen_floor(domain):
    calibration = read(f"results/benchmark_calibration_v1/{domain}/calibration.json")
    banks = {}
    for split in ("development", "confirmation"):
        requests = generate(calibration["low"], calibration["high"], calibration["median_window_mean"], split)
        assert len(requests) == 9
        for request in requests:
            assert statistics.mean(request["rates"]) == pytest.approx(calibration["median_window_mean"])
            assert min(request["rates"]) >= calibration["low"]-1e-12
            assert max(request["rates"]) <= calibration["high"]+1e-12
            assert request["control"] or request["constant_floor"] > .12
            assert request["qualified"] is False
        banks[split] = requests
    assert all(a["rates"] != b["rates"] for a, b in zip(banks["development"][:-1], banks["confirmation"][:-1]))
