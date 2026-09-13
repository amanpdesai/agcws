import json
import runpy

import pytest

from agcws.pipeline.model import cost
from agcws.pipeline.storage import write

module = runpy.run_path("analysis/flash_control_smoke.py")


def fixture(root, monkeypatch, api_failure):
    namespace = module["analyze"].__globals__
    monkeypatch.setitem(namespace, "source_inventory", lambda *args: {})

    class Backend:
        def payload(self, history, goal, n):
            return json.dumps([t["slot"] for t in history])

        def decode(self, text, n):
            return {"text": text, "n": n}

    monkeypatch.setitem(namespace, "backend", lambda domain: Backend())
    policies = ["flash-4096", "phase-random", "phase-ga"]
    write(root / "manifest.json", {"sources": {}, "spec": {
        "domain": "mesh-temporal", "budget": 6, "batch_size": 2, "seeds": [8200],
        "targets": {"flat_control": [1]*8}, "policies": policies,
        "stop_on_success": False, "scale": 1, "tolerance": .1}})
    write(root / "complete.json", {"slots": 18})
    write(root / "cache/measured/result.json", {"valid": True, "rates": [1]*8})
    for arm in policies:
        for start in (1, 3, 5):
            directory = root / f"panel/flat_control/8200/{arm}/batches/{start:03}"
            valid = not (api_failure and arm == "flash-4096" and start > 1)
            rows = [{"slot": slot, "program": {"slot": slot}, "valid": valid,
                     "rates": [1]*8 if valid else None, "loss": 0 if valid else None,
                     "cache_id": "measured" if valid else None, "stage": None if valid else "API"}
                    for slot in (start, start+1)]
            write(directory / "trials.json", rows)
            if arm == "flash-4096" and start > 1:
                write(directory / "input.json", {"payload": json.dumps(list(range(1, start)))})
                write(directory / "decoded.json", {"text": "{}", "n": 2})
                write(directory / "request_started.json", {"reservation_usd": .1})
                write(directory / "response.json", {
                    "raw_text": "{}", "usage_unknown": api_failure,
                    "tokens_in": None if api_failure else 10, "tokens_out": None if api_failure else 20,
                    "estimated_usd": None if api_failure else cost("flash-4096", 10, 20),
                    "model_version": None if api_failure else "gemini-2.5-flash",
                    "api_error": {"message": "schema rejected"} if api_failure else None})


@pytest.mark.parametrize("api_failure", [True, False])
def test_api_failure_history_is_not_measured_agent_feedback(tmp_path, monkeypatch, api_failure):
    fixture(tmp_path, monkeypatch, api_failure)
    result = module["analyze"](tmp_path)
    assert result["ready"] is not api_failure
    assert result["second_call_receives_prior_trial_history"] is True
    assert result["second_call_receives_measured_agent_feedback"] is not api_failure
    assert result["unknown_usage_reserved_usd"] == (.2 if api_failure else 0)


def test_missing_feedback_is_rejected(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch, False)
    path = tmp_path / "panel/flat_control/8200/flash-4096/batches/005/input.json"
    path.write_text(json.dumps({"payload": "[]"}))
    with pytest.raises(ValueError, match="measured history"):
        module["analyze"](tmp_path)
