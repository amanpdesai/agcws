import random

import pytest

from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.adapters.base import SimResult
from agcws.goals.loss import loss
from agcws.goals.schema import FixedTemporalGoal
from agcws.nodes.power import PowerProfile
from agcws.nodes.validation import validate_static
from agcws.workloads.schedule import ScheduleContract, expand_schedule, random_schedule
from agcws.workloads.structural_edits import (
    apply_structural_edit,
    random_structural_edit,
)


def test_random_structural_edits_preserve_budget_and_legality():
    contract = ScheduleContract(64, 6000)
    adapter = AESTemporalAdapter(contract)
    rng = random.Random(300)
    candidate = random_schedule(rng, contract)
    lengths = set()
    for _ in range(200):
        candidate = random_structural_edit(candidate, contract, rng)
        assert validate_static(adapter, candidate).valid
        lengths.add(len(expand_schedule(candidate, contract)))
    assert len(lengths) > 5


def test_bad_edit_does_not_mutate_parent_or_repair_budget():
    contract = ScheduleContract(64, 0)
    parent = {'sequence': [{'op': 'work', 'units': 64}]}
    with pytest.raises(ValueError, match='positive parts'):
        apply_structural_edit(parent, contract, {'op': 'split', 'a': 0, 'amount': 64})
    assert parent == {'sequence': [{'op': 'work', 'units': 64}]}


def test_fixed_scale_loss_preserves_amplitude_and_rejects_window_mismatch():
    goal = FixedTemporalGoal(windows=2, profile=[0, 100], scale=100, observation_cycles=10)
    profile = PowerProfile(0, 0, windowed=[0, 50], provenance={'clock_edges': 10})
    assert loss(profile, goal) == pytest.approx(0.5 / 2 ** 0.5)
    with pytest.raises(ValueError, match='window'):
        loss(PowerProfile(0, 0, windowed=[0, 100], provenance={'clock_edges': 11}), goal)
    assert loss(PowerProfile(0, 0, windowed=[0, 10000], provenance={'clock_edges': 10}), goal) == 1


def test_exact_work_and_static_stage_separation():
    adapter = AESTemporalAdapter(ScheduleContract(64, 0))
    assert validate_static(adapter, {}).stage.value == 'SCHEMA'
    assert validate_static(adapter, {'sequence': [{'op': 'work', 'units': 63}]}).stage.value == 'PROTOCOL'
    assert not adapter.validate_result(SimResult(True, True, True, 65)).valid
