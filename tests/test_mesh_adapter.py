import copy
import json
import random

import jsonschema

from agcws.adapters.mesh import MeshTemporalAdapter
from agcws.pipeline.mesh import MeshTemporal


def test_compact_phases_lower_deterministically_without_repair():
    backend = MeshTemporal()
    program = backend.random(random.Random(12))
    original = copy.deepcopy(program)
    adapter = backend.adapter()
    assert adapter.validate_schema(program).valid and adapter.validate_protocol(program).valid
    first = adapter.elaborate(program)
    assert first == adapter.elaborate(program) and program == original
    assert len(first["packets"]) == sum(p["packets"] for p in program["phases"])
    assert first["packets"] == sorted(first["packets"], key=lambda p: (p["release_cycle"], p["source"]))


def test_phase_random_spans_all_routes_and_varied_phase_counts():
    backend = MeshTemporal()
    rng = random.Random(12)
    programs = [backend.random(rng) for _ in range(100)]
    assert {p["route"] for w in programs for p in w["phases"]} == {"opposite", "neighbor", "self", "hotspot0"}
    assert len({len(w["phases"]) for w in programs}) > 25
    for program in programs:
        assert backend.adapter().validate_protocol(program).valid
        assert len(backend.adapter().elaborate(program)["packets"]) >= 64


def test_protocol_rejects_excess_work_and_impossible_phase_end():
    adapter = MeshTemporalAdapter()
    program = MeshTemporal().random(random.Random(12))
    program["phases"][0].update(start=8191, duration=2)
    assert not adapter.validate_protocol(program).valid
    program["phases"] = [dict(program["phases"][0], start=0, duration=1, packets=512)] * 9
    assert not adapter.validate_protocol(program).valid


def test_prompt_describes_actual_traffic_schema_not_aes_budgets():
    backend = MeshTemporal()
    schema = backend.schema(2)
    program = backend.random(random.Random(9))
    jsonschema.validate({"hypothesis": "test", "candidates": [program, program]}, schema)
    payload = json.loads(backend.payload([], {"profile": [0]*8}, 2))
    assert payload["design"]["name"] == "basejump_mesh_2x2"
    assert payload["response_schema"] == schema
    assert "64 work units" not in json.dumps(payload)


def test_failure_classifier_does_not_mask_infrastructure(tmp_path):
    backend = MeshTemporal()
    assert backend.failed(tmp_path) is None
    log = tmp_path / "run.log"
    log.write_text("unexpected simulator failure")
    assert backend.failed(tmp_path) is None
    log.write_text("MESH_INCOMPLETE sent=1 received=0 expected=64")
    assert backend.failed(tmp_path)["stage"] == "USEFUL_WORK"
    log.write_text("MESH_FUNCTIONAL_MISMATCH cycle=10 port=1 id=5")
    assert backend.failed(tmp_path)["stage"] == "FUNCTIONAL"
