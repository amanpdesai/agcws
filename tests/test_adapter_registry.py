from agcws.adapters import ADAPTERS, AESAdapter, AxiDmaAdapter, IbexAdapter


def test_adapter_registry_exposes_all_declared_designs():
    assert ADAPTERS == {
        AESAdapter.name: AESAdapter,
        AxiDmaAdapter.name: AxiDmaAdapter,
        IbexAdapter.name: IbexAdapter,
    }
