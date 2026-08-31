from agcws.policies.agent import OfflineAgent
from agcws.policies.hybrid import HybridSearch


def test_hybrid_policy_returns_requested_batch():
    agent = OfflineAgent(1)
    policy = HybridSearch(agent.proposer, seed=2, agent_fraction=0.5)
    candidates = policy.propose(None, None, [], 4)
    assert len(candidates) == 4
    assert all(candidate["operations"][0]["op"] == "configure" for candidate in candidates)
