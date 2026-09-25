import random

from agcws.designs.aes import AESAdapter


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
