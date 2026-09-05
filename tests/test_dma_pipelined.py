import random

from agcws.adapters.axi_dma.pipelined import PipelinedDmaAdapter, groups
from agcws.nodes.validation import validate_static


def test_pipelined_random_workloads_are_legal_and_meet_floor():
    adapter = PipelinedDmaAdapter()
    rng = random.Random(15)
    for _ in range(100):
        workload = adapter.random_workload(rng)
        assert validate_static(adapter, workload).valid
        assert sum(t['length'] for t in workload['transfers']) >= 4096


def test_groups_honor_each_member_credit():
    transfers = [{'outstanding': n} for n in [4, 4, 1, 8, 2, 2]]
    grouped = list(groups(transfers))
    assert [t for g in grouped for t in g] == transfers
    assert all(len(g) <= min(t['outstanding'] for t in g) for g in grouped)


def test_pipelined_validator_rejects_alias_and_out_of_range_memory():
    adapter = PipelinedDmaAdapter()
    for source, destination in [(0, 0), (65536, 4096), (0, 65536)]:
        workload = {'transfers': [{'src': source, 'dst': destination, 'length': 512}]}
        assert not validate_static(adapter, workload).valid


def test_pipelined_validator_rejects_permanent_backpressure():
    workload = {'transfers': [{'src': 0, 'dst': 4096, 'length': 512}],
                'backpressure': {'period': 8, 'read_pause': 8, 'write_pause': 0}}
    assert not validate_static(PipelinedDmaAdapter(), workload).valid
