from types import SimpleNamespace

import pytest

from agcws.pipeline.dma import DmaTemporal


def test_window_is_the_predeclared_corner_audit_choice():
    assert DmaTemporal.clock_edges == 9216


def test_deadline_failure_is_cached_without_score(tmp_path, monkeypatch):
    calls = []

    def failed_run(command, **kwargs):
        calls.append(command)
        assert "AGCWS_DMA_OBSERVATION_CYCLES=9216" in command
        kwargs["stdout"].write("AssertionError: workload failed to complete within the declared observation horizon\n")
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr("agcws.pipeline.schedule_backend.subprocess.run", failed_run)
    program = {"sequence": [{"op": "wait", "cycles": 6000}, {"op": "work", "units": 64}]}
    manifest = {"measurement_fingerprint": "test", "runtime": {"image_id": "test-image"}}
    result, hit = DmaTemporal().measured(program, tmp_path, manifest)
    assert not result["valid"] and result["stage"] == "FUNCTIONAL" and not hit
    assert "rates" not in result and "profile" not in result
    assert DmaTemporal().measured(program, tmp_path, manifest) == (result, True)
    assert len(calls) == 1


def test_unknown_tool_failure_is_not_relabelled_as_workload_invalid(tmp_path, monkeypatch):
    def failed_run(command, **kwargs):
        kwargs["stdout"].write("compiler unavailable\n")
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr("agcws.pipeline.schedule_backend.subprocess.run", failed_run)
    program = {"sequence": [{"op": "work", "units": 64}, {"op": "wait", "cycles": 6000}]}
    manifest = {"measurement_fingerprint": "test", "runtime": {"image_id": "test-image"}}
    with pytest.raises(RuntimeError, match="replay failed"):
        DmaTemporal().measured(program, tmp_path, manifest)
    assert not list((tmp_path / "cache").glob("*/result.json"))
