from .base import DesignAdapter, SimResult, Validity, ValidityStage
from .aes import AESAdapter
from .axi_dma import AxiDmaAdapter
from .ibex import IbexAdapter

ADAPTERS = {adapter.name: adapter for adapter in (AESAdapter, AxiDmaAdapter, IbexAdapter)}

__all__ = ["ADAPTERS", "AESAdapter", "AxiDmaAdapter", "DesignAdapter", "IbexAdapter",
           "SimResult", "Validity", "ValidityStage"]
