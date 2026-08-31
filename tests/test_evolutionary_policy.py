from types import SimpleNamespace

from agcws.policies.evolutionary import EvolutionarySearch


def test_evolutionary_policy_reuses_legal_elites():
    parent = {"operations": [{"op": "configure"}, {"op": "encrypt", "blocks": 24}]}
    trial = SimpleNamespace(workload=parent, profile=object(), validity=SimpleNamespace(valid=True), loss=0.1)
    candidate = EvolutionarySearch(2).propose(None, None, [trial], 3)
    assert len(candidate) == 3
    assert all(item["operations"][0]["op"] == "configure" for item in candidate)
