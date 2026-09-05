import json

from agcws.adapters.aes import AESAdapter
from agcws.adapters.base import Validity
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch
from agcws.policies.semantic import SemanticEvolution
from agcws.telemetry.ledger import Trial


def test_semantic_feedback_is_signed_and_omits_waveforms():
    goal = ScalarGoal(0.5)
    profile = PowerProfile(20, 30, useful_work=40, valid=True,
                           per_cycle_toggles=[999] * 10000)
    trial = Trial('t', 'aes', goal, 'random', 0, {}, Validity(True),
                  profile=profile, loss=0.25)
    agent = SemanticEvolution(lambda *_: '[]', 'test', model='fake').initialize(0, 10, 50)
    payload = agent.build_payload(AESAdapter(), goal, [trial], 4, 'test')
    data = json.loads(payload)
    assert data['parents_and_recent_feedback'][0]['achieved']['signed_residual'] == -0.25
    assert 'per_cycle_toggles' not in payload
    assert data['design']['minimum_useful_work'] == 38


def test_semantic_initialization_matches_random_without_model_call():
    def forbidden(*_):
        raise AssertionError('initialization called model')
    adapter = AESAdapter()
    goal = ScalarGoal(0.5)
    agent = SemanticEvolution(forbidden, 'test', model='fake').initialize(19, 10, 50)
    assert agent.propose(adapter, goal, [], 4) == RandomSearch(19).propose(adapter, goal, [], 4)
    assert agent.proposal_attempts == 1
