import pytest
import hashlib

from agcws.goals import ScalarGoal
from agcws.policies.vertex import VertexAgent, parse_candidates
from agcws.policies.vertex import build_payload
from agcws.adapters.base import Validity, ValidityStage
from agcws.telemetry.ledger import Trial


def test_vertex_boundary_parses_batched_json():
    agent = VertexAgent(lambda model, payload: '[{"operations": []}, {"operations": []}, {"operations": []}, {"operations": []}]', "system", model="fake")
    assert len(agent.propose(None, ScalarGoal(0.5), [], 4)) == 4
    assert agent.prompt_hash == hashlib.sha256(b"system").hexdigest()


def test_vertex_sampling_protocol_is_frozen():
    assert VertexAgent.temperature == 0.7
    assert VertexAgent.top_p == 0.95
    assert VertexAgent.max_output_tokens == 4096


def test_vertex_records_injected_usage_metadata():
    agent = VertexAgent(lambda *_: ('[{"operations": []}]', {"tokens_in": 12, "tokens_out": 7}),
                        "system", model="fake")
    agent.propose(None, ScalarGoal(0.5), [], 1)
    assert agent.last_usage == {"tokens_in": 12, "tokens_out": 7}


def test_vertex_boundary_rejects_non_json():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_candidates("not-json", 2)


def test_vertex_payload_serializes_nested_trial_values():
    trial = Trial("t0", "aes", ScalarGoal(0.5), "random", 3,
                  {"operations": []}, Validity(False, ValidityStage.PROTOCOL, "bad"))
    payload = build_payload(None, ScalarGoal(0.5), [trial], 2, "prompt")
    assert '"stage": "PROTOCOL"' in payload
    assert '"batch_size": 2' in payload
