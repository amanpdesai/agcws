import json

import pytest

from agcws.evaluation.power import panel
from agcws.reporting.metrics import key


def setup(tmp_path, monkeypatch):
    synthesis = tmp_path / "synthesis"
    synthesis.mkdir()
    (synthesis / "manifest.json").write_text("{}")
    body = {"inputs": {}, "cases": [{"id": "a", "domain": "aes-temporal"},
                                    {"id": "b", "domain": "aes-temporal"}], "omitted": []}
    plan = {**body, "sha256": key(body)}
    calls = []

    def run(plan, case_id, synthesis, out, **kwargs):
        calls.append(case_id)
        out.mkdir()
        (out / "measurement.json").write_text(json.dumps({"case_id": case_id, "plan_sha256": plan["sha256"]}))

    monkeypatch.setattr(panel, "run", run)
    return plan, {"aes-temporal": synthesis}, calls


def test_resume_skips_only_hash_verified_completions(tmp_path, monkeypatch):
    plan, mapping, calls = setup(tmp_path, monkeypatch)
    destination = tmp_path / "collection"
    assert panel.collect(plan, mapping, destination, workers=2)["all_passed"]
    assert sorted(calls) == ["a", "b"]
    result = panel.collect(plan, mapping, destination)
    assert all(c["status"] == "retained" for c in result["cases"])
    assert len(calls) == 2
    (destination / "a/attempt-001/measurement.json").write_text("{}")
    with pytest.raises(ValueError, match="changed"):
        panel.collect(plan, mapping, destination)


def test_changed_synthesis_cannot_mix_in_resumed_collection(tmp_path, monkeypatch):
    plan, mapping, calls = setup(tmp_path, monkeypatch)
    destination = tmp_path / "collection"
    panel.collect(plan, mapping, destination)
    (mapping["aes-temporal"] / "manifest.json").write_text('{"new": true}')
    with pytest.raises(ValueError, match="checkpoint differs"):
        panel.collect(plan, mapping, destination)
    assert len(calls) == 2


def test_failure_is_kept_and_other_cases_finish(tmp_path, monkeypatch):
    plan, mapping, calls = setup(tmp_path, monkeypatch)
    original = panel.run

    def fail(plan, case_id, synthesis, out, **kwargs):
        if case_id == "a":
            raise ValueError("functional mismatch")
        return original(plan, case_id, synthesis, out, **kwargs)

    monkeypatch.setattr(panel, "run", fail)
    destination = tmp_path / "collection"
    result = panel.collect(plan, mapping, destination)
    assert not result["all_passed"]
    assert (destination / "a/attempt-001/failure.json").exists()
    assert not (destination / "a/complete.json").exists()
    assert calls == ["b"]
    monkeypatch.setattr(panel, "run", original)
    assert panel.collect(plan, mapping, destination)["all_passed"]
    assert (destination / "a/attempt-002/measurement.json").exists()
    assert calls == ["b", "a"]


def test_no_implicit_synthesis_mapping(tmp_path):
    body = {"inputs": {}, "cases": [{"domain": "ibex-temporal"}], "omitted": []}
    plan = {**body, "sha256": key(body)}
    with pytest.raises(ValueError, match="missing synthesis"):
        panel.collect(plan, {}, tmp_path / "collection")
    assert not (tmp_path / "collection").exists()


def test_preflight_failure_defers_rest_and_resume_retains_success(tmp_path, monkeypatch):
    plan, mapping, calls = setup(tmp_path, monkeypatch)
    original = panel.run

    def fail(*args, **kwargs):
        raise ValueError('readiness failure')

    monkeypatch.setattr(panel, 'run', fail)
    destination = tmp_path / 'collection'
    result = panel.collect(plan, mapping, destination, workers=2, preflight=True)
    assert [c['status'] for c in result['cases']] == ['failed', 'deferred']
    assert not result['all_passed'] and not calls
    monkeypatch.setattr(panel, 'run', original)
    assert panel.collect(plan, mapping, destination, workers=2, preflight=True)['all_passed']
    assert sorted(calls) == ['a', 'b']
    assert panel.collect(plan, mapping, destination, preflight=True)['all_passed']
    assert len(calls) == 2
