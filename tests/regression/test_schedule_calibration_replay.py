import pytest

from agcws.core.storage import write
from agcws.evidence.calibration_replay import audit


@pytest.mark.parametrize("change", [None, "rates", "per_cycle_toggles", "normalization"])
def test_calibration_bridge_checks_values_and_integer_trace(tmp_path, monkeypatch, change):
    original, replay = tmp_path / "original", tmp_path / "replay"
    for root in (original, replay):
        write(root / "manifest.json", {"runtime": root.name})
        rows = [{"slot": i, "program": {"jobs": 1}, "valid": True,
                 "stage": None, "reason": None, "rates": [2]*8,
                 "profile": {"useful_work": 1024}, "cache_id": str(i)} for i in range(64)]
        if root == replay and change == "rates":
            rows[0]["rates"][0] = 3
        write(root / "panel/target/seed/random/batches/0/trials.json", rows)
        for i in range(64):
            trace = {"clock_edges": 8, "per_cycle_toggles": [2]*8,
                     "window_toggles": [2]*8, "total_transitions": 16}
            if root == replay and i == 0 and change == "per_cycle_toggles":
                trace["per_cycle_toggles"] = [1, 3] + [2]*6
            write(root / f"cache/{i}/attempt-1/activity.json", trace)
    monkeypatch.setitem(audit.__globals__, "verify_inputs", lambda *_: {"measurement_fingerprint": "new"})
    monkeypatch.setitem(audit.__globals__, "report", lambda root: {
        "measurement_fingerprint": root.name,
        "scale": 3 if root == replay and change == "normalization" else 2})
    if change:
        with pytest.raises(ValueError, match="differs|changed"):
            audit(original, replay)
    else:
        result = audit(original, replay)
        assert result["cases"] == 64
        assert result["exact_integer_activity_match"]
        assert not result["full_study_ready"]
