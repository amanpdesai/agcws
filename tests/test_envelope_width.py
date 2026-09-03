import random

from agcws.adapters.axi_dma import AxiDmaAdapter
from agcws.adapters.ibex import IbexAdapter


def test_dma_random_workloads_span_transfer_volume():
    adapter = AxiDmaAdapter()
    values = [sum(t["length"] for t in adapter.random_workload(random.Random(i))["transfers"])
              for i in range(40)]
    assert max(values) - min(values) >= 10 * 1024


def test_ibex_random_workloads_span_program_length():
    adapter = IbexAdapter()
    values = [len(adapter.random_workload(random.Random(i))["program"]) for i in range(40)]
    assert max(values) - min(values) >= 5_000
