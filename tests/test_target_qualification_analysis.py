import runpy

import pytest

from agcws.pipeline.storage import write
from agcws.pipeline.targets import requests

analyze = runpy.run_path("analysis/target_qualification.py")["analyze"]


def fixture(tmp_path, *, fingerprint="frozen"):
    bank_path = tmp_path / "bank.json"
    requested = requests(0, 100, split="development")
    write(bank_path, {"calibration": {"scale": 100, "domain": "mesh-temporal", "measurement_fingerprint": "frozen"},
                      "splits": {"development": {"requests": requested}}})
    write(tmp_path / "manifest.json", {"measurement_fingerprint": fingerprint, "spec": {
        "targets": {r["id"]: r["rates"] for r in requested}, "scale": 100, "tolerance": 0.1,
        "budget": 256, "batch_size": 2, "seeds": [7300], "policies": ["phase-random", "phase-ga"],
        "stop_on_success": False, "domain": "mesh-temporal"}})
    write(tmp_path / "complete.json", {"slots": 4608})
    for request in requested:
        write(tmp_path / "cache" / request["id"] / "result.json", {
            "valid": True, "profile": {"window_rates": request["rates"]}})
        for arm in ("phase-random", "phase-ga"):
            write(tmp_path / "panel" / request["id"] / "7300" / arm / "batches/001/trials.json",
                  [{"slot": slot, "valid": True, "loss": 0.0, "rates": request["rates"],
                    "cache_id": request["id"], "program": {}} for slot in range(1, 257)])
    return bank_path


def test_qualification_uses_frozen_vectors_and_deterministic_tie_break(tmp_path):
    bank = fixture(tmp_path)
    result = analyze(tmp_path, bank, "development")
    assert result["qualified_nonflat"] == 8 and result["qualified_controls"] == 1
    assert all(r["witness"]["policy"] == "phase-ga" and r["witness"]["slot"] == 1 for r in result["requests"])


def test_changed_measurement_contract_cannot_qualify_old_requests(tmp_path):
    bank = fixture(tmp_path, fingerprint="changed")
    with pytest.raises(ValueError, match="contract changed"):
        analyze(tmp_path, bank, "development")
