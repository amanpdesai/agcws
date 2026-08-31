from types import SimpleNamespace

from agcws.policies.evolutionary import EvolutionarySearch


def test_evolutionary_policy_prefers_lower_loss_elite():
    better = {"operations": [{"op": "configure"}, {"op": "encrypt", "blocks": 16}]}
    worse = {"operations": [{"op": "configure"}, {"op": "encrypt", "blocks": 32}]}
    history = [
        SimpleNamespace(workload=worse, profile=object(), validity=SimpleNamespace(valid=True), loss=0.8),
        SimpleNamespace(workload=better, profile=object(), validity=SimpleNamespace(valid=True), loss=0.1),
    ]
    policy = EvolutionarySearch(seed=4, elite_size=1)
    proposals = policy.propose(None, None, history, 4)
    assert len(proposals) == 4
    assert all(candidate["operations"][1]["blocks"] == 16 for candidate in proposals)
