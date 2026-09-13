import runpy

import pytest

from agcws.adapters.redmule import RedmuleTemporalAdapter
from agcws.pipeline.storage import write

module = runpy.run_path("scripts/probe_redmule_pacing.py")


def test_fixed_probe_is_balanced_legal_and_not_target_selected():
    cases = module["programs"]()
    assert len(cases) == len({case["id"] for case in cases}) == 54
    adapter = RedmuleTemporalAdapter()
    for case in cases:
        program = case["program"]
        releases = adapter.elaborate(program)
        assert len(releases)*program["size"]**3 >= adapter.useful_work_floor
        assert min(releases) == 2048 and max(releases) < 51200
    assert cases == module["programs"]()


def test_probe_resume_reuses_results_and_rejects_source_drift(tmp_path, monkeypatch):
    namespace = module["prepare"].__globals__
    measurement = {"spec": {"domain": "redmule-temporal"}}
    monkeypatch.setitem(namespace, "verify_inputs", lambda *args: measurement)
    calls = []

    class FakeBackend:
        def measured(self, program, root, manifest):
            key = str(len(calls))
            calls.append(program)
            result = {"valid": True, "cache_id": key}
            write(root / "cache" / key / "result.json", result)
            return result, False

    monkeypatch.setitem(namespace, "RedmuleTemporal", FakeBackend)
    root = tmp_path / "probe"
    module["prepare"](tmp_path, root)
    assert module["run"](tmp_path, root)["valid"] == 54
    assert module["run"](tmp_path, root)["valid"] == 54
    assert len(calls) == 54
    monkeypatch.setitem(namespace, "verify_inputs", lambda *args: {"changed": True})
    with pytest.raises(ValueError, match="inputs changed"):
        module["run"](tmp_path, root)
