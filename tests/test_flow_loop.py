from flows.loop import LoopState, propose_batch
from agcws.adapters.aes import AESAdapter
from agcws.goals import ScalarGoal
from agcws.policies.agent import AgentPolicy


def test_flow_charges_failed_proposal_batch():
    policy = AgentPolicy(lambda *_: (_ for _ in ()).throw(ValueError("bad JSON")))
    state = LoopState(ScalarGoal(0.5), policy, budget=3)
    assert propose_batch(state, AESAdapter(), 3) == []
    assert state.proposal_index == 3
    assert propose_batch(state, AESAdapter(), 3) == []
