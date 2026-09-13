import runpy

from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import requests

module = runpy.run_path("scripts/qualify_redmule_pulses.py")


def test_measured_failure_cannot_be_admitted_by_good_prediction(tmp_path, monkeypatch):
    namespace = module["prepare"].__globals__
    measurement = {"measurement_fingerprint": "same"}
    monkeypatch.setitem(namespace, "verify_inputs", lambda *args: measurement)
    probe = tmp_path / "probe"
    write(probe / "manifest.json", {"measurement": measurement})
    write(probe / "complete.json", {"cases": 54})
    for pattern in ("zeros", "alternating", "random"):
        write(probe / "panel" / f"size16-{pattern}-x1-queued" / "result.json",
              {"measurement": {"cache_id": pattern}})
        directory = probe / "cache" / pattern / "attempt-001"
        write(directory / "functional.json", {"valid": True, "completed_jobs": 1,
                                               "job_completions": [[0, 4096, 0]]})
        write(directory / "activity.json", {"per_cycle_toggles": [2]*2048+[10]*2048+[2]*61440})
    bank = tmp_path / "bank.json"
    write(bank, {"calibration": {"measurement_fingerprint": "same", "scale": 100},
                 "splits": {s: {"requests": requests(0, 100, split=s)}
                            for s in ("development", "confirmation")}})

    class FakeBackend:
        def measured(self, *args):
            return {"valid": False, "stage": "USEFUL_WORK"}, False

    monkeypatch.setitem(namespace, "RedmuleTemporal", FakeBackend)
    root = tmp_path / "witness"
    assert module["prepare"](tmp_path, probe, bank, root)["prepared_cases"] == 432
    result = module["run"](tmp_path, root)
    assert len(result["reports"]) == 18
    assert all(not row["qualified"] and row["reasons"] == ["invalid_witness"] for row in result["reports"])
    assert read(root / "complete.json") == result
