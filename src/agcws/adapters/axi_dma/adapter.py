"""Descriptor-driven legality boundary for the verilog-axi DMA adapter."""
from __future__ import annotations

from agcws.adapters.base import DesignAdapter, SimResult, Validity, ValidityStage


class AxiDmaAdapter(DesignAdapter):
    name = "verilog_axi_dma"
    design_summary = ("verilog-axi DMA moves memory blocks through independent read and write channels. "
                      "Activity changes with transfer lengths, descriptor count, channel concurrency, "
                      "and backpressure gaps across the descriptor engine and channels.")
    protocol_constraints = ("addresses are aligned and stay within mapped memory", "length is positive and <= 1 MiB",
                            "transfers cannot cross a 4 KiB boundary", "outstanding depth is 1..8",
                            "gap_cycles is 0..10000")
    useful_work_floor = 4096
    regions = ["read_channel", "write_channel", "descriptor_engine"]
    workload_schema = {"type": "object", "required": ["transfers"],
                       "properties": {"transfers": {"type": "array", "maxItems": 128,
                       "items": {"type": "object", "properties": {
                           "src": {"type": "integer", "minimum": 0}, "dst": {"type": "integer", "minimum": 0},
                           "length": {"type": "integer", "minimum": 1, "maximum": 1048576},
                           "outstanding": {"type": "integer", "minimum": 1, "maximum": 8},
                           "gap_cycles": {"type": "integer", "minimum": 0, "maximum": 10000}},
                           "required": ["src", "dst", "length"], "additionalProperties": False}}},
                       "additionalProperties": False}
    data_width_bytes = 8
    max_transfer = 1 << 20
    channel_depth = 8

    def random_workload(self, rng) -> dict:
        """Generate a legal, non-idle baseline workload for the generic policy."""
        transfers = []
        pacing = rng.choice(("back_to_back", "light_gap", "bursty", "sparse"))
        gap_range = {"back_to_back": (0, 0), "light_gap": (1, 8),
                     "bursty": (0, 40), "sparse": (80, 400)}[pacing]
        remaining = rng.randrange(self.useful_work_floor, 32 * 1024 + 1, 256)
        minimum_count = max(4, (remaining + 4095) // 4096)
        count = rng.randint(minimum_count, min(8, remaining // 256))
        for index in range(count):
            slots_left = count - index - 1
            minimum = max(256, remaining - slots_left * 4096)
            maximum = min(4096, remaining - slots_left * 256)
            length = rng.randrange(minimum // 256, maximum // 256 + 1) * 256
            remaining -= length
            src_page = (index % 4) * 0x1000
            dst_page = (index % 4 + 4) * 0x1000
            src_offset = rng.randrange(0, 0x1000 - length + 1, 8)
            dst_offset = rng.randrange(0, 0x1000 - length + 1, 8)
            transfers.append({"src": src_page + src_offset,
                              "dst": dst_page + dst_offset,
                              "length": length,
                              "gap_cycles": rng.randint(*gap_range)})
        if remaining:
            transfers[-1]["length"] += remaining
            length = transfers[-1]["length"]
            transfers[-1]["src"] = (count - 1) % 4 * 0x1000 + rng.randrange(0, 0x1000 - length + 1, 8)
            transfers[-1]["dst"] = ((count - 1) % 4 + 4) * 0x1000 + rng.randrange(0, 0x1000 - length + 1, 8)
        return {"transfers": transfers}

    def mutate_workload(self, workload: dict, rng) -> dict:
        """Mutate DMA addresses/lengths while preserving protocol legality."""
        import copy
        candidate = copy.deepcopy(workload)
        index = rng.randrange(len(candidate["transfers"]))
        transfer = candidate["transfers"][index]
        transfer["src"] = 0x400 + rng.randrange(9) * 0x100
        transfer["src"] &= ~0x7
        transfer["dst"] = 0x1000 + rng.randrange(12) * 0x100
        transfer["dst"] &= ~0x7
        return candidate

    def validate_schema(self, workload: dict) -> Validity:
        if not isinstance(workload, dict):
            return Validity(False, ValidityStage.SCHEMA, "workload must be an object")
        if set(workload) - {"transfers"}:
            return Validity(False, ValidityStage.SCHEMA, "unknown workload field")
        transfers = workload.get("transfers") if isinstance(workload, dict) else None
        if not isinstance(transfers, list) or len(transfers) > 128:
            return Validity(False, ValidityStage.SCHEMA, "transfers must contain at most 128 items")
        if any(not isinstance(item, dict) for item in transfers):
            return Validity(False, ValidityStage.SCHEMA, "each transfer must be an object")
        if any(set(item) - {"src", "dst", "length", "outstanding", "gap_cycles"} for item in transfers):
            return Validity(False, ValidityStage.SCHEMA, "unknown transfer field")
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
            gap_cycles = transfer.get("gap_cycles", 0)
            if not isinstance(gap_cycles, int) or gap_cycles < 0 or gap_cycles > 10_000:
                return Validity(False, ValidityStage.PROTOCOL, "gap_cycles out of range")
        return Validity(True)

    def elaborate(self, workload: dict) -> list[dict]:
        return workload["transfers"]

    def useful_work(self, result: SimResult) -> float:
        return result.useful_work
