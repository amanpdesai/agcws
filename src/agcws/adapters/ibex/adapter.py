"""Instruction-stream legality boundary for the Ibex adapter."""
from __future__ import annotations

from agcws.adapters.base import DesignAdapter, SimResult, Validity, ValidityStage


class IbexAdapter(DesignAdapter):
    name = "ibex"
    useful_work_floor = 10_000
    regions = ["fetch", "decode", "execute", "load_store"]
    workload_schema = {"type": "object", "required": ["program"],
                       "properties": {"program": {"type": "array", "maxItems": 200_000},
                                      "memory_size": {"type": "integer", "minimum": 4}},
                       "additionalProperties": False}
    memory_size = 1 << 20
    supported_ops = {"add", "addi", "and", "or", "xor", "lw", "sw", "beq", "bne", "nop", "ecall"}

    def validate_schema(self, workload: dict) -> Validity:
        program = workload.get("program") if isinstance(workload, dict) else None
        if not isinstance(program, list) or not program or len(program) > 200_000:
            return Validity(False, ValidityStage.SCHEMA, "program must contain 1..200000 instructions")
        if any(not isinstance(instruction, dict) for instruction in program):
            return Validity(False, ValidityStage.SCHEMA, "each instruction must be an object")
        return Validity(True)

    def validate_protocol(self, workload: dict) -> Validity:
        program = workload["program"]
        has_termination = False
        for index, instruction in enumerate(program):
            op = instruction.get("op")
            if op not in self.supported_ops:
                return Validity(False, ValidityStage.PROTOCOL, f"unsupported instruction: {op}")
            if op in {"lw", "sw"}:
                address = instruction.get("address")
                if not isinstance(address, int) or address < 0 or address + 4 > self.memory_size:
                    return Validity(False, ValidityStage.PROTOCOL, "load/store address outside mapped memory")
                if address % 4:
                    return Validity(False, ValidityStage.PROTOCOL, "load/store address must be word aligned")
            if op in {"beq", "bne"}:
                target = instruction.get("target")
                if not isinstance(target, int) or target < 0 or target >= len(program) * 4 or target % 4:
                    return Validity(False, ValidityStage.PROTOCOL, "branch target outside aligned program")
            if op == "ecall":
                has_termination = True
        if not has_termination:
            return Validity(False, ValidityStage.PROTOCOL, "program must contain a reachable termination instruction")
        return Validity(True)

    def elaborate(self, workload: dict) -> list[dict]:
        return workload["program"]

    def useful_work(self, result: SimResult) -> float:
        return result.useful_work
