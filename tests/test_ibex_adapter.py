from agcws.adapters.base import ValidityStage
from agcws.adapters.ibex import IbexAdapter
import random


def program(*instructions):
    return {"program": list(instructions)}


def test_ibex_accepts_legal_terminated_program():
    result = IbexAdapter().validate_protocol(program({"op": "lw", "address": 0}, {"op": "ecall"}))
    assert result.valid


def test_ibex_rejects_unaligned_memory_access():
    result = IbexAdapter().validate_protocol(program({"op": "sw", "address": 2}, {"op": "ecall"}))
    assert result.stage is ValidityStage.PROTOCOL


def test_ibex_requires_termination():
    result = IbexAdapter().validate_protocol(program({"op": "nop"}))
    assert result.stage is ValidityStage.PROTOCOL


def test_ibex_generators_preserve_useful_work_and_termination():
    adapter = IbexAdapter()
    workload = adapter.random_workload(random.Random(7))
    assert len(workload["program"]) >= adapter.useful_work_floor + 1
    assert workload["program"][-1] == {"op": "ecall"}
    mutated = adapter.mutate_workload(workload, random.Random(8))
    assert mutated["program"][-1] == {"op": "ecall"}
    assert adapter.validate_schema(mutated).valid
    assert adapter.validate_protocol(mutated).valid
