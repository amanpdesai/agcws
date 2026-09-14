import json
import runpy

import pytest

from agcws.pipeline.model import cost


def test_readiness_accounting_checks_liability_and_unknown_errors(tmp_path, monkeypatch):
    fixture = runpy.run_path("tests/test_bank_smoke_audit.py")["fixture"]
    analyze = fixture(tmp_path, monkeypatch, 7)
    (tmp_path / "manifest.json").write_text(json.dumps(analyze.__globals__["verify_inputs"](None, None)))
    complete = tmp_path / "complete.json"
    complete.write_text(json.dumps({"cells": 54, "slots": 864,
                                    "liability_usd": 126*cost("flash-4096", 10, 20)}))
    accounting = runpy.run_path("analysis/full_flash_readiness.py")["accounting"]
    result = accounting(tmp_path)
    assert len(result["feedback_targets"]) == 18
    assert result["unknown_reserved_usd"] == 0
    response = tmp_path / "panel/t0/8501/flash-4096/batches/003/response.json"
    contents = json.loads(response.read_text())
    contents["api_error"] = {"type": "ServerError", "message": "500 unknown failure"}
    response.write_text(json.dumps(contents))
    with pytest.raises(ValueError, match="unaccounted API"):
        accounting(tmp_path)
