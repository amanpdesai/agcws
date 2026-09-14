import json
import runpy

import pytest

from agcws.pipeline.storage import read, write
from agcws.workloads.schedule import ScheduleContract

driver = runpy.run_path("scripts/refine_schedule_witnesses.py")


def setup_run(root, monkeypatch, *, replay_rates=None):
    namespace = driver["run"].__globals__
    measurement = {"frozen": True}
    monkeypatch.setitem(namespace, "verify_inputs", lambda *args: measurement)
    cache, executed = {}, []

    class Design:
        contract = ScheduleContract(64, 6000)

        def measured(self, program, *args):
            key = json.dumps(program, sort_keys=True)
            if key in cache:
                return cache[key], True
            executed.append(key)
            rates = ([1]*8 if program.get("solve") else [0]*8)
            if replay_rates is not None and program.get("parent"):
                rates = replay_rates
            result = {"valid": True, "rates": rates}
            cache[key] = result
            return result, False

    monkeypatch.setitem(namespace, "backend", lambda domain: Design())
    write(root / "manifest.json", {
        "kind": "aes-schedule-witness-refinement-v3", "domain": "aes-temporal",
        "measurement": measurement, "driver_sources": driver["sources"](), "max_workers": 1,
        "budget": 260, "paired_batches": 128,
        "bank": {"calibration": {"scale": 1}}, "cases": [{"id": "control", "seed": 0,
            "request": {"rates": [1]*8, "control": True}, "rates": [0]*8,
            "program": {"parent": True},
            "initial_candidates": [{"solve": True}, {"solve": False}, {"solve": False, "third": True}]}]})
    write(root / "freeze.json", {"manifest_sha256": driver["sha"](root / "manifest.json")})
    return executed


def test_all_seed_proposals_charged_before_stopping_and_resume_cached(tmp_path, monkeypatch):
    executed = setup_run(tmp_path, monkeypatch)
    assert driver["run"](tmp_path, tmp_path)["qualified"] == 1
    assert len(executed) == 4
    assert read(tmp_path / "panel/control/complete.json")["charged_slots"] == 4
    assert len(read(tmp_path / "panel/control/seeds.json")["rows"]) == 3
    assert not list((tmp_path / "panel/control").glob("batch-*.json"))
    assert driver["run"](tmp_path, tmp_path)["qualified"] == 1
    assert len(executed) == 4


def test_parent_replay_drift_stops_before_new_proposals(tmp_path, monkeypatch):
    executed = setup_run(tmp_path, monkeypatch, replay_rates=[.1]*8)
    with pytest.raises(ValueError, match="exact replay"):
        driver["run"](tmp_path, tmp_path)
    assert len(executed) == 1
    assert not (tmp_path / "complete.json").exists()


def test_modified_manifest_fails_before_measurement(tmp_path, monkeypatch):
    executed = setup_run(tmp_path, monkeypatch)
    with (tmp_path / "manifest.json").open("a") as stream:
        stream.write("\n")
    with pytest.raises(ValueError, match="manifest changed"):
        driver["run"](tmp_path, tmp_path)
    assert not executed
