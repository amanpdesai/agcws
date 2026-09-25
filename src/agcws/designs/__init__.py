"""Generic command-oriented adapters, distinct from the temporal study registry.

Use temporal_registry.backend for the five-design benchmark interfaces.
"""

from agcws.core.contracts import DesignAdapter, SimResult, Validity, ValidityStage
from agcws.designs.aes import AESAdapter
from agcws.designs.dma import AxiDmaAdapter
from agcws.designs.ibex import IbexAdapter

GENERIC_ADAPTERS = {adapter.name: adapter for adapter in (AESAdapter, AxiDmaAdapter, IbexAdapter)}

__all__ = ["GENERIC_ADAPTERS", "AESAdapter", "AxiDmaAdapter", "DesignAdapter", "IbexAdapter",
           "SimResult", "Validity", "ValidityStage"]
