import random

import pytest

from agcws.adapters.axi_dma.pipelined import groups
from agcws.adapters.axi_dma.temporal import DmaTemporalAdapter, lower_schedule
from agcws.adapters.base import SimResult
from agcws.workloads.schedule import ScheduleContract, random_schedule


def test_dma_lowering_preserves_work_idle_and_group_boundaries():
    contract = ScheduleContract(64, 6000)
    for seed in range(30):
        schedule = random_schedule(random.Random(seed), contract)
        lowered = lower_schedule(schedule, contract)
        transfers = lowered['workload']['transfers']
        assert len(transfers) == 64
        assert sum(t['length'] for t in transfers) == 4096
        assert sum(t['gap_cycles'] for t in transfers) + lowered['trailing_idle_cycles'] == 6000
        assert all(len(g) <= 8 for g in groups(transfers))


def test_split_changes_concurrency_not_work():
    contract = ScheduleContract(64, 0)
    together = lower_schedule({'sequence': [{'op': 'work', 'units': 64}]}, contract)
    separate = lower_schedule({'sequence': [{'op': 'repeat', 'count': 64,
                                            'body': [{'op': 'work', 'units': 1}]}]}, contract)
    assert [len(g) for g in groups(together['workload']['transfers'])] == [8] * 8
    assert [len(g) for g in groups(separate['workload']['transfers'])] == [1] * 64


def test_work_units_convert_to_bytes_and_keep_hard_floor():
    adapter = DmaTemporalAdapter(ScheduleContract(64, 6000))
    assert adapter.useful_work_floor == 4096
    assert adapter.validate_result(SimResult(True, True, True, 4096)).valid
    assert not adapter.validate_result(SimResult(True, True, True, 64)).valid
    assert not adapter.validate_result(SimResult(True, True, True, 8192)).valid
    with pytest.raises(ValueError, match='64..128'):
        DmaTemporalAdapter(ScheduleContract(1, 0))
