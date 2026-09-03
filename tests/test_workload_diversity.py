import random

from agcws.adapters.aes import AESAdapter
from agcws.adapters.axi_dma import AxiDmaAdapter
from agcws.adapters.ibex import IbexAdapter
from agcws.policies.random_search import RandomSearch
from agcws.policies.agent import OfflineAgent
from agcws.goals.schema import ScalarGoal


def test_aes_random_workloads_span_schedule_dimensions():
    adapter = AESAdapter()
    workloads = [adapter.random_workload(random.Random(seed)) for seed in range(40)]
    totals = {sum(op.get("blocks", 0) for op in w["operations"]) for w in workloads}
    gaps = {sum(op.get("cycles", 0) for op in w["operations"]) for w in workloads}
    assert len(totals) > 20
    assert len(gaps) > 5
    assert all(adapter.validate_protocol(w).valid for w in workloads)
    assert all(sum(op.get("cycles", 0) for op in w["operations"]) <= 10_000
               for w in workloads)


def test_offline_agent_is_not_random_alias_for_scalar_goal():
    adapter = AESAdapter()
    agent = OfflineAgent(seed=7)
    candidates = agent.propose(adapter, ScalarGoal(q=0.9, tolerance=0.05), [], 4)
    totals = [sum(op.get("blocks", 0) for op in w["operations"]) for w in candidates]
    assert all(total >= adapter.useful_work_floor for total in totals)
    assert len(set(totals)) >= 2


def test_offline_agent_is_not_random_alias_for_dma_or_ibex():
    goal = ScalarGoal(q=0.5, tolerance=0.05)
    for adapter in (AxiDmaAdapter(), IbexAdapter()):
        random_candidates = RandomSearch(seed=11).propose(adapter, goal, [], 3)
        agent_candidates = OfflineAgent(seed=11).propose(adapter, goal, [], 3)
        assert [repr(item) for item in agent_candidates] != [repr(item) for item in random_candidates]
