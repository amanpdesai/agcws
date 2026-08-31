from agcws.policies.agent import AgentPolicy, OfflineAgent


def test_agent_policy_batches_and_caps_output():
    policy = AgentPolicy(lambda *_: [{"id": 1}, {"id": 2}, {"id": 3}])
    assert policy.propose(None, None, [], 2) == [{"id": 1}, {"id": 2}]


def test_offline_agent_is_reproducible():
    first = OfflineAgent(8).propose(None, None, [], 3)
    second = OfflineAgent(8).propose(None, None, [], 3)
    assert first == second
    assert all(item["operations"][0]["op"] == "configure" for item in first)
