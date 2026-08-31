from agcws.adapters.base import ValidityStage
from agcws.adapters.ibex import IbexAdapter


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
