"""Descriptor-driven legality boundary for the verilog-axi DMA adapter."""
from __future__ import annotations

from agcws.adapters.base import DesignAdapter, SimResult, Validity, ValidityStage


class AxiDmaAdapter(DesignAdapter):
    name = "verilog_axi_dma"
    useful_work_floor = 4096
    regions = ["read_channel", "write_channel", "descriptor_engine"]
    workload_schema = {"type": "object", "required": ["transfers"],
                       "properties": {"transfers": {"type": "array", "maxItems": 128}},
                       "additionalProperties": False}
    data_width_bytes = 8
    max_transfer = 1 << 20
    channel_depth = 8

    def validate_schema(self, workload: dict) -> Validity:
        transfers = workload.get("transfers") if isinstance(workload, dict) else None
        if not isinstance(transfers, list) or len(transfers) > 128:
            return Validity(False, ValidityStage.SCHEMA, "transfers must contain at most 128 items")
        if any(not isinstance(item, dict) for item in transfers):
            return Validity(False, ValidityStage.SCHEMA, "each transfer must be an object")
        return Validity(True)

    def validate_protocol(self, workload: dict) -> Validity:
        for transfer in workload["transfers"]:
            for field in ("src", "dst", "length"):
                if not isinstance(transfer.get(field), int):
                    return Validity(False, ValidityStage.PROTOCOL, f"{field} must be an integer")
            if transfer["length"] <= 0 or transfer["length"] > self.max_transfer:
                return Validity(False, ValidityStage.PROTOCOL, "transfer length out of range")
            if transfer["src"] % self.data_width_bytes or transfer["dst"] % self.data_width_bytes:
                return Validity(False, ValidityStage.PROTOCOL, "addresses must be data-width aligned")
            if (transfer["src"] & 0xfff) + transfer["length"] > 0x1000:
                return Validity(False, ValidityStage.PROTOCOL, "transfer crosses an AXI 4KB boundary")
            outstanding = transfer.get("outstanding", 1)
            if not isinstance(outstanding, int) or outstanding < 1 or outstanding > self.channel_depth:
                return Validity(False, ValidityStage.PROTOCOL, "channel depth exceeded")
        return Validity(True)

    def elaborate(self, workload: dict) -> list[dict]:
        return workload["transfers"]

    def useful_work(self, result: SimResult) -> float:
        return result.useful_work
