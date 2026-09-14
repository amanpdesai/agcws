import runpy

import pytest

from agcws.pipeline.storage import read


def test_bank_smoke_rejects_stale_fingerprint():
    config = runpy.run_path("scripts/prepare_bank_smoke.py")["config"]
    bank = read("results/dma/qualified-bank-v1.json")
    with pytest.raises(ValueError, match="current measurement"):
        config(bank, {"spec": {"domain": "dma-temporal"}, "measurement_fingerprint": "wrong"})


def test_bank_smoke_has_all_targets_and_matched_arms():
    config = runpy.run_path("scripts/prepare_bank_smoke.py")["config"]
    bank = read("results/dma/qualified-bank-v1.json")
    spec = read("results/dma/window-v3/calibration-config.json")
    result = config(bank, {"spec": spec, "measurement_fingerprint": bank["calibration"]["measurement_fingerprint"],
                           "runtime": {"image_id": spec["image"]}})
    assert len(result["targets"]) == 18 and result["budget"] == 6
    assert result["policies"] == ["flash-4096", "phase-random", "phase-ga"]
    assert result["stop_on_success"] is False
