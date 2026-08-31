import pytest

from agcws.goals import ScalarGoal
from agcws.policies.vertex import VertexAgent, parse_candidates


def test_vertex_boundary_parses_batched_json():
    agent = VertexAgent(lambda model, payload: '[{"operations": []}]', "system", model="fake")
    assert len(agent.propose(None, ScalarGoal(0.5), [], 4)) == 1


def test_vertex_boundary_rejects_non_json():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_candidates("not-json", 2)
