import json
import random
import threading
from pathlib import Path

import jsonschema
import pytest

from agcws.core.storage import read, write
from agcws.designs.aes.backend import AesTemporal
from agcws.designs.temporal_registry import backend
from agcws.designs.workloads.schedule import ScheduleContract, expand_schedule, random_schedule
from agcws.search.providers.gemini import MODELS
from agcws.search.schedules import crossover, decode, propose_classical, response_schema
from agcws.studies import engine
from agcws.studies.spec import validate


def test_schedule_ga_preserves_contract_and_parent_visibility():
    contract = ScheduleContract(64, 6000)
    rng = random.Random(7101)
    history = []
    for i in range(200):
        program, parents = propose_classical("phase-ga", rng, history, contract)
        expanded = expand_schedule(program, contract)
        assert all(parent < i + 1 for parent in parents)
        history.append({"slot": i + 1, "program": program, "valid": True,
                        "loss": len(expanded) / 100})
    assert len({json.dumps(row["program"]) for row in history}) > 100


def test_crossover_inherits_each_parents_resource_partition():
    contract = ScheduleContract(4, 100)
    left = {"sequence": [{"op": "work", "units": 4}, {"op": "wait", "cycles": 100}]}
    right = {"sequence": [{"op": "wait", "cycles": 20}, {"op": "work", "units": 2},
                          {"op": "wait", "cycles": 80}, {"op": "work", "units": 2}]}
    sequence = crossover(left, right, contract, random.Random(0))["sequence"]
    assert [n["units"] for n in sequence if n["op"] == "work"] == [4]
    assert [n["cycles"] for n in sequence if n["op"] == "wait"] == [20, 80]


def test_response_schema_and_short_batch_keep_slots():
    contract = ScheduleContract(64, 6000)
    candidate = random_schedule(random.Random(1), contract)
    schema = response_schema(2, contract)
    jsonschema.validate({"hypothesis": "test", "candidates": [candidate, candidate]}, schema)
    assert "$ref" not in json.dumps(schema)
    decoded = decode(json.dumps({"hypothesis": "test", "candidates": [candidate]}), 2)
    assert decoded["slots"][0]["submitted"] == candidate
    assert decoded["slots"][1]["submitted"] is None
    assert decoded["response_error"]
    assert all(s["submitted"] is None for s in decode('{"candidates": [NaN]}', 2)["slots"])


def test_aes_source_backend_requires_explicit_null_binary():
    spec = json.loads(Path("tests/fixtures/study_example.json").read_text())
    spec.update(domain="aes-temporal", binary=None)
    assert validate(spec) == spec
    spec["policies"] = ["gest-pool4"]
    with pytest.raises(ValueError, match="not implemented"):
        validate(spec)


def test_bad_schedule_never_invokes_simulator(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("static rejection must not execute Docker")
    monkeypatch.setattr("agcws.designs.schedule_backend.subprocess.run", forbidden)
    backend = AesTemporal()
    for program, stage in [(None, "SCHEMA"), ({"sequence": [{"op": "work", "units": 1}]}, "PROTOCOL")]:
        result, hit = backend.measured(program, tmp_path, {})
        assert not result["valid"] and result["stage"] == stage and not hit


@pytest.mark.parametrize("domain", ["aes-temporal", "dma-temporal"])
def test_shared_feedback_rounds_use_only_completed_history(tmp_path, domain):
    spec = read(Path("tests/fixtures/study_example.json"))
    spec.update(domain=domain, binary=None, budget=8, batch_size=2, policies=["flash-4096"])
    design = backend(domain)
    manifest = {"spec": validate(spec), "schema": design.schema(2)}
    write(tmp_path / "manifest.json", manifest)

    class Meter:
        halted = threading.Event()
        calls = 0

        def call(self, directory, arm, contents, schema, identity):
            self.calls += 1
            payload = json.loads(contents)
            assert [t["slot"] for t in payload["history"]] == list(range(1, identity["first_slot"]))
            assert payload["design"]["summary"] and payload["design"]["protocol_constraints"]
            assert all(t["residual"] == [0.3] * 8 for t in payload["history"])
            candidate = design.random(random.Random(self.calls))
            return {"model_version": MODELS[arm], "raw_text": json.dumps({
                "hypothesis": "Revise the pacing", "candidates": [candidate, candidate]})}

    def measured(proposal, *args):
        expand_schedule(proposal["submitted"], design.contract)
        return {"valid": True, "loss": 0.3, "residual": [0.3] * 8, "rates": [30] * 8}

    meter = Meter()
    result = engine.cell(tmp_path, manifest, "example", 10, "flash-4096", meter, measured)
    assert meter.calls == 3 and result["valid_slots"] == 8
