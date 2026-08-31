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
