import runpy

from agcws.pipeline.storage import read, write


def test_planner_retains_failed_requests_and_never_launches(tmp_path, monkeypatch):
    prepare = runpy.run_path("scripts/prepare_target_bank.py")["prepare"]
    monkeypatch.setitem(prepare.__globals__, "report", lambda path: {
        "status": "calibrated", "low": 2.0, "high": 100.0, "scale": 98.0,
        "median_window_mean": 15.0})
    write(tmp_path / "manifest.json", {"spec": {
        "name": "calibration", "domain": "aes-temporal", "targets": {"calibration_only": [0.0]*8},
        "seeds": [7200, 7201], "policies": ["random"], "budget": 32, "batch_size": 2,
        "scale": 1.0, "tolerance": 0.1, "binary": None, "image": "test-image", "max_workers": 2,
        "cost_ceiling_usd": 1.0, "stop_on_success": False}, "runtime": {"image_id": "frozen-image"}})
    out = tmp_path / "bank"
    result = prepare(tmp_path, out)
    assert not result["executed"]
    for split in ("development", "confirmation"):
        assert result["splits"][split]["necessary_floor_failures"]
        assert result["splits"][split]["requests"] == 9
        spec = read(out / f"{split}.json")
        assert set(spec["policies"]) == {"phase-random", "phase-ga"}
        assert spec["budget"] == 256 and spec["image"] == "frozen-image"
        assert len(spec["targets"]) == 9
    bank = read(out / "requested_bank.json")
    assert not bank["qualified"]
    assert len(bank["splits"]["development"]["pairwise_distances"]) == 36
