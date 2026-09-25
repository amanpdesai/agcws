from pathlib import Path

from agcws.designs import GENERIC_ADAPTERS, AESAdapter, AxiDmaAdapter, IbexAdapter


def test_adapter_registry_exposes_all_declared_designs():
    assert GENERIC_ADAPTERS == {
        AESAdapter.name: AESAdapter,
        AxiDmaAdapter.name: AxiDmaAdapter,
        IbexAdapter.name: IbexAdapter,
    }


def test_non_aes_adapter_contracts_document_harness_boundary():
    architecture = Path("docs/ARCHITECTURE.md").read_text()
    for design in ("AXI DMA", "Ibex"):
        assert design in architecture
    assert "harness" in architecture.lower()
    assert "schema" in architecture and "measurement contract" in architecture
