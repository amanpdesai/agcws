"""Infrastructure failures do not consume model proposal slots."""

import pytest
from httpx import ReadTimeout
from test_pipeline_engine import evaluate, manifest

from agcws.core.storage import read
from agcws.search.providers import recovery
from agcws.studies import engine


def test_engine_pauses_without_scoring_transport_failure(tmp_path, monkeypatch):
    tmp_path = tmp_path / "study"
    tmp_path.mkdir()
    spec = manifest(tmp_path, "pro-4096", budget=4)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr(engine, "verify_inputs", lambda *_: spec)
    original = engine.cell
    monkeypatch.setattr(engine, "cell", lambda *args: original(*args, evaluator=evaluate))

    def fail(*args):
        raise ReadTimeout("injected transport failure")

    monkeypatch.setattr(recovery, "generate", fail)
    with pytest.raises(recovery.InfrastructurePause):
        engine.run(tmp_path, tmp_path, allow_paid=True)
    batch = tmp_path / "panel/example/0/pro-4096/batches/003"
    assert (batch / "attempts/001/response.json").exists()
    assert not (batch / "response.json").exists()
    assert not (batch / "proposals.json").exists()
    assert not (batch / "trials.json").exists()
    assert not (tmp_path / "complete.json").exists()
    assert engine.status(tmp_path)["completed_slots"] == 2
    assert recovery.RecoveryMeter(tmp_path, 100).liability > 0
    assert read(tmp_path.parent / "provider-paused.json")["version"] == recovery.VERSION
