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


def test_vertex_boundary_rejects_non_json():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_candidates("not-json", 2)


def test_vertex_payload_serializes_nested_trial_values():
    trial = Trial("t0", "aes", ScalarGoal(0.5), "random", 3,
                  {"operations": []}, Validity(False, ValidityStage.PROTOCOL, "bad"))
    payload = build_payload(None, ScalarGoal(0.5), [trial], 2, "prompt")
    assert '"stage": "PROTOCOL"' in payload
    assert '"batch_size": 2' in payload
