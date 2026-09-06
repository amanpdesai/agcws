import random

import pytest

from agcws.adapters.aes.temporal import lower_schedule
from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.nodes.validation import validate_static
from agcws.workloads.schedule import ScheduleContract, expand_schedule, random_schedule


def test_repeat_matches_explicit_sequence():
    body = [{'op': 'work', 'units': 8}, {'op': 'wait', 'cycles': 750}]
    contract = ScheduleContract(64, 6000)
    compact = {'sequence': [{'op': 'repeat', 'count': 8, 'body': body}]}
    explicit = {'sequence': body * 8}
    assert expand_schedule(compact, contract) == expand_schedule(explicit, contract)
    assert lower_schedule(compact, contract) == lower_schedule(explicit, contract)
    assert validate_static(AESTransactionAdapter(), lower_schedule(compact, contract)).valid


def test_random_schedules_preserve_exact_budgets_and_are_deterministic():
    contract = ScheduleContract(64, 6000)
    for seed in range(100):
        schedule = random_schedule(random.Random(seed), contract)
        assert schedule == random_schedule(random.Random(seed), contract)
        assert expand_schedule(schedule, contract)
        assert validate_static(AESTransactionAdapter(), lower_schedule(schedule, contract)).valid


@pytest.mark.parametrize('node', [
    {'op': 'work', 'units': True}, {'op': 'wait', 'cycles': -1},
    {'op': 'repeat', 'count': 0, 'body': []}, {'op': 'unknown'},
    {'op': 'work', 'units': 64, 'extra': 1},
])
def test_invalid_schema_never_materializes(node):
    with pytest.raises(ValueError):
        expand_schedule({'sequence': [node]}, ScheduleContract(64, 0))


def test_budget_violation_and_expansion_bomb_rejected():
    with pytest.raises(ValueError, match='useful-work'):
        expand_schedule({'sequence': [{'op': 'work', 'units': 1}]}, ScheduleContract(64, 0))
    node = {'op': 'work', 'units': 1}
    for _ in range(3):
        node = {'op': 'repeat', 'count': 64, 'body': [node]}
    with pytest.raises(ValueError, match='operation limit'):
        expand_schedule({'sequence': [node]}, ScheduleContract(64, 0))
    for _ in range(10):
        node = {'op': 'repeat', 'count': 1, 'body': [node]}
    with pytest.raises(ValueError, match='depth'):
        expand_schedule({'sequence': [node]}, ScheduleContract(64, 0))


def test_idle_mismatch_is_not_silently_repaired():
    with pytest.raises(ValueError, match='idle-cycle'):
        expand_schedule({'sequence': [{'op': 'work', 'units': 64}]}, ScheduleContract(64, 6000))


def test_json_schema_integral_numbers_lower_to_integer_counts():
    schedule = {'sequence': [{'op': 'repeat', 'count': 2.0,
                              'body': [{'op': 'work', 'units': 32.0}]}]}
    expanded = expand_schedule(schedule, ScheduleContract(64, 0))
    assert expanded == [{'op': 'work', 'units': 32}] * 2
    assert all(type(op['units']) is int for op in expanded)
