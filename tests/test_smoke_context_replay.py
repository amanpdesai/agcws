import runpy

import pytest

from agcws.pipeline.storage import write


@pytest.mark.parametrize("failure", ["budget", "fingerprint"])
def test_context_replay_rejects_wrong_protocol_or_current_bank(tmp_path, monkeypatch, failure):
    audit = runpy.run_path("analysis/smoke_context_replay.py")["audit"]
    bank = {"domain": "mesh-temporal", "target_bank_qualified": True,
            "calibration": {"measurement_fingerprint": "expected", "scale": 10},
            "splits": {s: {"requests": [{"id": str(i), "rates": [2]*8} for i in range(9)]}
                       for s in ("development", "confirmation")}}
    targets = {f"{s}-{r['id']}": r["rates"] for s, part in bank["splits"].items() for r in part["requests"]}
    write(tmp_path / "bank.json", bank)
    write(tmp_path / "manifest.json", {"spec": {"domain": "mesh-temporal", "targets": targets,
        "scale": 10, "budget": 24 if failure == "budget" else 16, "batch_size": 2,
        "seeds": [8502], "stop_on_success": False, "policies": ["flash-4096", "phase-random", "phase-ga"]}})
    monkeypatch.setitem(audit.__globals__, "verify_inputs", lambda *_: {
        "measurement_fingerprint": "wrong" if failure == "fingerprint" else "expected"})
    with pytest.raises(ValueError, match="v4 smoke settings|current reference"):
        audit(tmp_path, tmp_path, tmp_path / "bank.json")
