"""Instruction-stream legality boundary for the Ibex adapter."""
from __future__ import annotations

import copy
import random

from agcws.adapters.base import DesignAdapter, SimResult, Validity, ValidityStage


class IbexAdapter(DesignAdapter):
    name = "ibex"
    design_summary = ("Ibex is a RISC-V instruction-stream processor. ALU, branch, load/store, and "
                      "fetch behavior shape activity; memory addresses and instruction mix are the main knobs.")
    protocol_constraints = ("instructions must be supported by the configured ISA", "loads/stores stay in mapped aligned memory",
                            "branch targets are aligned and in range", "a reachable ecall termination is required")
    useful_work_floor = 10_000
    regions = ["fetch", "decode", "execute", "load_store"]
    activity_region_prefixes = {
        "fetch": ("fetch", "instr", "pc"),
        "decode": ("decode", "opcode", "imm"),
        "execute": ("alu", "branch", "csr"),
        "load_store": ("load", "store", "mem", "lsu"),
    }
    workload_schema = {"type": "object", "required": ["program"],
                       "properties": {"program": {"type": "array", "maxItems": 200_000, "items": {"oneOf": [
                                      {"type": "object", "properties": {"op": {"enum": ["nop", "add", "and", "or", "xor", "ecall"]}}, "required": ["op"], "additionalProperties": False},
                                      {"type": "object", "properties": {"op": {"const": "addi"}, "immediate": {"type": "integer", "minimum": -2048, "maximum": 2047}}, "required": ["op", "immediate"], "additionalProperties": False},
                                      {"type": "object", "properties": {"op": {"enum": ["lw", "sw"]}, "address": {"type": "integer", "minimum": 0}}, "required": ["op", "address"], "additionalProperties": False},
                                      {"type": "object", "properties": {"op": {"enum": ["beq", "bne"]}, "target": {"type": "integer", "minimum": 0}}, "required": ["op", "target"], "additionalProperties": False}
                                  ]}},
                                      "memory_size": {"type": "integer", "minimum": 4}},
                       "additionalProperties": False}
    # Matches the upstream simple-system linker: 192 KiB of RAM at 0x100000.
    memory_size = 0x30000
    data_base = 0x20000
    supported_ops = {"add", "addi", "and", "or", "xor", "lw", "sw", "beq", "bne", "nop", "ecall"}

    def validate_schema(self, workload: dict) -> Validity:
        if not isinstance(workload, dict):
            return Validity(False, ValidityStage.SCHEMA, "workload must be an object")
        if set(workload) - {"program", "memory_size"}:
            return Validity(False, ValidityStage.SCHEMA, "unknown workload field")
        if not isinstance(workload.get("memory_size", self.memory_size), int) or workload.get("memory_size", self.memory_size) < 4:
            return Validity(False, ValidityStage.SCHEMA, "memory_size must be an integer >= 4")
        program = workload.get("program") if isinstance(workload, dict) else None
        if not isinstance(program, list) or not program or len(program) > 200_000:
            return Validity(False, ValidityStage.SCHEMA, "program must contain 1..200000 instructions")
        if any(not isinstance(instruction, dict) for instruction in program):
            return Validity(False, ValidityStage.SCHEMA, "each instruction must be an object")
        allowed = {"lw": {"op", "address"}, "sw": {"op", "address"},
                   "beq": {"op", "target"}, "bne": {"op", "target"}}
        for instruction in program:
            op = instruction.get("op")
            if op in allowed and set(instruction) - allowed[op]:
                return Validity(False, ValidityStage.SCHEMA, "unknown instruction field")
        return Validity(True)

    def validate_protocol(self, workload: dict) -> Validity:
        program = workload["program"]
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
        # Presence alone is not enough: a self-loop or an earlier unconditional
        # control-flow trap must not satisfy the termination contract.
        reachable = {0}
        pending = [0]
        while pending:
            index = pending.pop()
            instruction = program[index]
            if instruction["op"] == "ecall":
                return Validity(True)
            successors = []
            if instruction["op"] in {"beq", "bne"}:
                successors.append(instruction["target"] // 4)
            if index + 1 < len(program):
                successors.append(index + 1)
            for successor in successors:
                if successor not in reachable:
                    reachable.add(successor)
                    pending.append(successor)
        return Validity(False, ValidityStage.PROTOCOL,
                        "program must contain a reachable termination instruction")

    def elaborate(self, workload: dict) -> list[dict]:
        return workload["program"]

    def useful_work(self, result: SimResult) -> float:
        return result.useful_work

    def random_workload(self, rng: random.Random) -> dict:
        """Generate a legal, terminating instruction-stream candidate."""
        # The simple-system runtime retires a few setup/control-flow
        # instructions outside the generated body.  Keep a margin so the
        # measured counter remains above the hard useful-work floor.
        # Vary dynamic instruction mix and runtime well beyond the old narrow
        # 256-instruction band; normalization needs a real behavioral spread.
        length = rng.randint(self.useful_work_floor + 64, 20_000)
        # Choose a workload family first.  Uniformly sampling individual
        # instructions makes every long program converge to the same mix and
        # collapses the activity envelope.  Structured families preserve legal
        # termination while exercising materially different datapaths.
        families = (
            ("idle", ("nop",) * 7 + ("addi",)),
            ("alu", ("addi", "add", "and", "or", "xor") * 3 + ("nop",)),
            ("memory", ("lw", "sw") * 3 + ("addi", "nop")),
            ("mixed", ("nop", "addi", "add", "and", "or", "xor", "lw", "sw")),
        )
        _, ops = rng.choice(families)
        program = []
        for _ in range(length):
            op = rng.choice(ops)
            if op in {"lw", "sw"}:
                instruction = {"op": op, "address": rng.randrange(self.data_base, self.memory_size - 3, 4)}
            elif op == "addi":
                instruction = {"op": op, "immediate": rng.randint(-16, 16)}
            else:
                instruction = {"op": op}
            program.append(instruction)
        program.append({"op": "ecall"})
        return {"program": program, "memory_size": self.memory_size}

    def mutate_workload(self, workload: dict, rng: random.Random) -> dict:
        """Mutate one stream while retaining its terminating ecall."""
        candidate = copy.deepcopy(workload)
        program = candidate["program"]
        body = program[:-1] if program and program[-1].get("op") == "ecall" else program
        if not body:
            return self.random_workload(rng)
        index = rng.randrange(len(body))
        op = rng.choice(("nop", "addi", "add", "and", "or", "xor", "lw", "sw"))
        if op in {"lw", "sw"}:
            body[index] = {"op": op, "address": rng.randrange(self.data_base, self.memory_size - 3, 4)}
        elif op == "addi":
            body[index] = {"op": op, "immediate": rng.randint(-16, 16)}
        else:
            body[index] = {"op": op}
        candidate["program"] = body + [{"op": "ecall"}]
        return candidate
