import copy
import json
import runpy

from agcws.pipeline.storage import read, write

pair = runpy.run_path("analysis/witness_refinement.py")["pair"]
driver = runpy.run_path("scripts/refine_witnesses.py")


def test_pair_keeps_parent_and_opposite_edit_even_when_one_is_illegal():
    program = {"phases": [{"start": 0, "duration": 1, "jobs": 1}]}
    original = copy.deepcopy(program)
    left, right = pair(program, 0, 0)
    assert program == original
    assert left["phases"][0]["start"] == -256
    assert right["phases"][0]["start"] == 256
    assert pair(program, 0, 0) == [left, right]


def test_actual_pair_is_charged_before_success_and_resume_is_cached(tmp_path, monkeypatch):
    namespace = driver["run"].__globals__
    measurement = {"frozen": True}
    monkeypatch.setitem(namespace, "verify_inputs", lambda *args: measurement)
    cache, executions = {}, []

    class Backend:
        def measured(self, program, *args):
            key = json.dumps(program, sort_keys=True)
            if key in cache:
                return cache[key], True
            executions.append(key)
            start = program["phases"][0]["start"]
            result = {"valid": False, "stage": "SCHEMA"} if start < 0 else {"valid": True, "rates": [start/256]*8}
            cache[key] = result
            return result, False

    monkeypatch.setitem(namespace, "backend", lambda domain: Backend())
    write(tmp_path / "manifest.json", {
        "kind": "measured-witness-refinement-v4", "domain": "redmule-temporal",
        "measurement": measurement, "driver_sources": driver["sources"](), "max_workers": 1,
        "bank": {"calibration": {"scale": 1}}, "cases": [{"id": "control", "seed": 0,
            "request": {"rates": [1]*8, "control": True}, "rates": [0]*8,
            "program": {"phases": [{"start": 0, "duration": 1, "jobs": 1}]}}]})
    write(tmp_path / "freeze.json", {"manifest_sha256": driver["sha"](tmp_path / "manifest.json")})
    assert driver["run"](tmp_path, tmp_path)["qualified"] == 1
    result = read(tmp_path / "panel/control/complete.json")
    assert result["charged_slots"] == 3
    rows = read(tmp_path / "panel/control/batch-000.json")["rows"]
    assert rows[0]["measurement"]["valid"] is False
    assert rows[1]["measurement"]["valid"] is True
    assert driver["run"](tmp_path, tmp_path)["qualified"] == 1
    assert len(executions) == 3
