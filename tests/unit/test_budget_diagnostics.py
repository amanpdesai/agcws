import copy
import json
import random

import pytest

from agcws.designs.temporal_registry import backend
from agcws.designs.workloads.schedule import (
    ScheduleContract,
    budget_diagnostics,
    expand_schedule,
    random_schedule,
)

CONTRACT = ScheduleContract(64, 6000)


def test_repeat_multiplicity_and_deficit_without_repair():
    program = {"sequence": [{"op": "repeat", "count": 2, "body": [
        {"op": "work", "units": 32}, {"op": "wait", "cycles": 2375}]}]}
    original = copy.deepcopy(program)
    result = budget_diagnostics(program, CONTRACT)
    assert result["actual"] == {"work_units": 64, "idle_cycles": 4750, "expanded_operations": 4}
    assert result["required_minus_actual"] == {"work_units": 0, "idle_cycles": 1250}
    assert program == original
    with pytest.raises(ValueError, match="idle-cycle budget"):
        expand_schedule(program, CONTRACT)


def test_totals_match_expansion_for_random_valid_workloads():
    rng = random.Random(9400)
    for _ in range(100):
        program = random_schedule(rng, CONTRACT)
        expanded = expand_schedule(program, CONTRACT)
        totals = budget_diagnostics(program, CONTRACT)
        assert totals["actual"] == {"work_units": sum(n.get("units", 0) for n in expanded),
                                    "idle_cycles": sum(n.get("cycles", 0) for n in expanded),
                                    "expanded_operations": len(expanded)}
        assert totals["required_minus_actual"] == {"work_units": 0, "idle_cycles": 0}


def test_large_repeat_is_counted_without_expanding_or_marking_valid():
    program = {"sequence": [{"op": "repeat", "count": 64, "body": [
        {"op": "repeat", "count": 64, "body": [{"op": "wait", "cycles": 10000}]}]}]}
    result = budget_diagnostics(program, CONTRACT)
    assert result["actual"]["expanded_operations"] == 4096
    assert result["expanded_operation_limit_exceeded"]
    assert result["required_minus_actual"]["idle_cycles"] < 0


def test_payload_diagnostic_does_not_mutate_history_or_invent_numbers():
    history = [{"slot": 1, "program": {"wrong": True}, "valid": False,
                "stage": "SCHEMA", "reason": "unknown key", "loss": None}]
    original = copy.deepcopy(history)
    for domain in ("aes-temporal", "dma-temporal"):
        value = json.loads(backend(domain).payload(history, {"profile": [2]*8, "scale": 10, "tolerance": .1}, 2))
        assert "actual" not in value["history"][0]["budget_arithmetic"]
        assert value["history"][0]["valid"] is False
    assert history == original
