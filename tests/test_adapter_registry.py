from agcws.adapters import ADAPTERS, AESAdapter, AxiDmaAdapter, IbexAdapter


def test_adapter_registry_exposes_all_declared_designs():
    assert ADAPTERS == {
        AESAdapter.name: AESAdapter,
        AxiDmaAdapter.name: AxiDmaAdapter,
        IbexAdapter.name: IbexAdapter,
    }
from pathlib import Path


def test_non_aes_adapter_contracts_document_harness_boundary():
    for name in ("axi_dma", "ibex"):
        readme = Path("src/agcws/adapters") / name / "README.md"
        assert readme.is_file()
        assert "harness" in readme.read_text().lower()
