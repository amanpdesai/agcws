from agcws.adapters.aes import AESAdapter
from agcws.policies.agent import OfflineAgent
from agcws.policies.random_search import RandomSearch


def _blocks(workload: dict) -> int:
    return sum(int(op.get("blocks", 0)) for op in workload["operations"]
               if op.get("op") in {"encrypt", "decrypt"})


def test_random_policy_respects_adapter_work_floor():
    workloads = RandomSearch(3).propose(AESAdapter(), None, [], 32)
    assert all(_blocks(workload) >= AESAdapter.useful_work_floor for workload in workloads)


def test_offline_agent_respects_adapter_work_floor():
    workloads = OfflineAgent(3).propose(AESAdapter(), None, [], 32)
    assert all(_blocks(workload) >= AESAdapter.useful_work_floor for workload in workloads)
