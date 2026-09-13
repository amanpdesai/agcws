import statistics

import pytest

from agcws.pipeline.calibration import DOMAINS, plan
from agcws.pipeline.storage import read
from agcws.pipeline.targets import mean_matched_requests


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
