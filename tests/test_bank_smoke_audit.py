import json
import runpy

import pytest

from agcws.pipeline.model import cost
from agcws.pipeline.provider_schema import provenance
from agcws.pipeline.storage import write


def fixture(root, monkeypatch, first_valid):
    analyze = runpy.run_path("analysis/bank_smoke.py")["analyze"]
    policies = ["flash-4096", "phase-random", "phase-ga"]
    manifest = {"spec": {"domain": "mesh-temporal", "budget": 16, "batch_size": 2,
        "seeds": [8501], "targets": {f"t{i}": [1]*8 for i in range(18)},
        "stop_on_success": False, "scale": 1, "tolerance": .1, "policies": policies}}
    monkeypatch.setitem(analyze.__globals__, "verify_inputs", lambda *args: manifest)

    class Backend:
        def schema(self, n):
            return {"type": "object"}

        def payload(self, history, goal, n):
            return json.dumps([t["slot"] for t in history])

        def decode(self, text, n):
            return {"text": text, "n": n}

    monkeypatch.setitem(analyze.__globals__, "backend", lambda *args: Backend())
    write(root / "complete.json", {"slots": 864, "cells": 54})
    write(root / "cache/measured/result.json", {"valid": True, "profile": {"window_rates": [1]*8}})
    schema = provenance(Backend().schema(2))
    for target in manifest["spec"]["targets"]:
        for arm in policies:
            for start in range(1, 16, 2):
                directory = root / "panel" / target / "8501" / arm / "batches" / f"{start:03}"
                valid = arm != "flash-4096" or start == 1 or start >= first_valid
                write(directory / "trials.json", [{"slot": slot, "program": {"slot": slot},
                    "valid": valid, "stage": None if valid else "PROTOCOL", "loss": 0 if valid else None,
                    "cache_id": "measured" if valid else None, "rates": [1]*8 if valid else None}
                    for slot in (start, start+1)])
                if arm == "flash-4096" and start > 1:
                    write(directory / "input.json", {"payload": json.dumps(list(range(1, start)))})
                    write(directory / "decoded.json", {"text": "{}", "n": 2})
                    write(directory / "request_started.json", {"reservation_usd": .1, "schema_provenance": schema})
                    write(directory / "response.json", {"raw_text": "{}", "usage_unknown": False,
                        "tokens_in": 10, "tokens_out": 20, "estimated_usd": cost("flash-4096", 10, 20),
                        "model_version": "gemini-2.5-flash", "schema_provenance": schema})
    return analyze


@pytest.mark.parametrize(("first_valid", "ready"), [(3, True), (7, True), (15, False), (17, False)])
def test_measured_generated_candidate_must_reach_a_later_call(tmp_path, monkeypatch, first_valid, ready):
    audit = fixture(tmp_path, monkeypatch, first_valid)(tmp_path)
    assert audit["ready"] is ready
    assert audit["targets_ready"] == (18 if ready else 0)
    assert audit["charged_slots"] == 864


def test_changed_feedback_payload_fails_closed(tmp_path, monkeypatch):
    analyze = fixture(tmp_path, monkeypatch, 7)
    path = tmp_path / "panel/t0/8501/flash-4096/batches/009/input.json"
    path.write_text(json.dumps({"payload": "[]"}))
    with pytest.raises(ValueError, match="feedback payload"):
        analyze(tmp_path)


@pytest.mark.parametrize(("error_type", "stage", "operational"), [
    ("ServerError", "API", True), ("TransportError", "API", False),
    ("ServerError", "SCHEMA", False),
])
def test_operational_gate_preserves_strict_failure(tmp_path, monkeypatch, error_type, stage, operational):
    analyze = fixture(tmp_path, monkeypatch, 7)
    batch = tmp_path / "panel/t0/8501/flash-4096/batches/003"
    response = json.loads((batch / "response.json").read_text())
    response.update(raw_text="", usage_unknown=True, estimated_usd=None,
                    api_error={"type": error_type, "message": "504 DEADLINE_EXCEEDED. test"})
    (batch / "response.json").write_text(json.dumps(response))
    (batch / "decoded.json").write_text(json.dumps({"text": "", "n": 2}))
    trials = json.loads((batch / "trials.json").read_text())
    for trial in trials:
        trial["stage"] = stage
    (batch / "trials.json").write_text(json.dumps(trials))
    result = analyze(tmp_path)
    assert result["ready"] is False
    assert result["operational_ready"] is operational
    assert result["unknown_reserved_usd"] == .1


def test_orphan_request_fails_operational_audit(tmp_path, monkeypatch):
    analyze = fixture(tmp_path, monkeypatch, 7)
    write(tmp_path / "panel/t0/8501/flash-4096/batches/099/request_started.json", {})
    with pytest.raises(ValueError, match="unresolved or unexpected"):
        analyze(tmp_path)
