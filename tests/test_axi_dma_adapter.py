from agcws.adapters.axi_dma import AxiDmaAdapter
from agcws.adapters.base import ValidityStage


def transfer(**overrides):
    value = {"src": 0x1000, "dst": 0x2000, "length": 4096}
    value.update(overrides)
    return value


def test_axi_dma_accepts_aligned_transfer():
    assert AxiDmaAdapter().validate_protocol({"transfers": [transfer()]}).valid


def test_axi_dma_rejects_unaligned_address():
    result = AxiDmaAdapter().validate_protocol({"transfers": [transfer(src=3)]})
    assert result.stage is ValidityStage.PROTOCOL


def test_axi_dma_rejects_four_kilobyte_crossing():
    result = AxiDmaAdapter().validate_protocol({"transfers": [transfer(src=0x1ff8, length=16)]})
    assert result.stage is ValidityStage.PROTOCOL


def test_axi_dma_allows_many_sequential_descriptors():
    result = AxiDmaAdapter().validate_protocol({"transfers": [transfer(src=i * 0x1000, dst=0x2000, length=4096)
                                                                  for i in range(9)]})
    assert result.valid


def test_axi_dma_rejects_true_outstanding_depth_overflow():
    result = AxiDmaAdapter().validate_protocol({"transfers": [transfer(outstanding=9)]})
    assert result.stage is ValidityStage.PROTOCOL


def test_axi_dma_random_workloads_are_diverse_and_above_floor():
    import random

    adapter = AxiDmaAdapter()
    workloads = [adapter.random_workload(random.Random(seed)) for seed in range(4)]
    assert len({str(workload) for workload in workloads}) == 4
    for workload in workloads:
        assert sum(item["length"] for item in workload["transfers"]) >= adapter.useful_work_floor
        assert adapter.validate_schema(workload).valid
        assert adapter.validate_protocol(workload).valid
        assert all(item["src"] + item["length"] <= 0x10000 for item in workload["transfers"])
        assert all(item["dst"] + item["length"] <= 0x10000 for item in workload["transfers"])


def test_axi_dma_random_workloads_vary_transaction_pacing():
    import random
    workloads = [AxiDmaAdapter().random_workload(random.Random(seed)) for seed in range(40)]
    gaps = {item.get("gap_cycles", 0) for workload in workloads for item in workload["transfers"]}
    assert len(gaps) > 10
