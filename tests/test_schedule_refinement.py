import copy
import runpy

import pytest

from agcws.workloads.schedule import ScheduleContract, expand_schedule

paired_transfer = runpy.run_path("analysis/schedule_refinement.py")["paired_transfer"]
initial_schedules = runpy.run_path("analysis/schedule_refinement.py")["initial_schedules"]


def test_wait_transfers_preserve_totals_parent_and_determinism():
    contract = ScheduleContract(work_units=64, idle_cycles=6000)
    program = {"sequence": [{"op": "wait", "cycles": 3000},
                            {"op": "work", "units": 64},
                            {"op": "wait", "cycles": 3000}]}
    original = copy.deepcopy(program)
    for batch in range(128):
        proposals = paired_transfer(program, contract, batch, 8300)
        assert proposals == paired_transfer(program, contract, batch, 8300)
        for proposal in proposals:
            sequence = expand_schedule(proposal, contract)
            assert sum(n.get("cycles", 0) for n in sequence) == 6000
            assert sum(n.get("units", 0) for n in sequence) == 64
        assert sum(p["sequence"][0]["cycles"] for p in proposals) == 6000
    assert program == original


def test_illegal_transfer_remains_visible_not_clamped_or_retried():
    contract = ScheduleContract(work_units=64, idle_cycles=6000)
    program = {"sequence": [{"op": "work", "units": 1},
                            {"op": "wait", "cycles": 6000},
                            {"op": "work", "units": 63}]}
    left, right = paired_transfer(program, contract, 0, 0)
    assert left["sequence"][0]["units"] == 0
    with pytest.raises(ValueError):
        expand_schedule(left, contract)
    assert expand_schedule(right, contract)[0]["units"] == 2


def test_single_group_requires_explicit_structural_proposal():
    contract = ScheduleContract(work_units=64, idle_cycles=6000)
    program = {"sequence": [{"op": "work", "units": 64},
                            {"op": "wait", "cycles": 6000}]}
    with pytest.raises(ValueError, match="two work or two wait"):
        paired_transfer(program, contract, 0, 0)


@pytest.mark.parametrize("rates", [[23]*8, [2, 2, 2, 85, 85, 2, 2, 2],
                                   [2, 10, 15, 20, 30, 35, 40, 50]])
def test_initializations_are_distinct_legal_fixed_resource_proposals(rates):
    contract = ScheduleContract(64, 6000)
    candidates = initial_schedules(rates, 2, contract, 6774)
    assert len(candidates) == 3
    assert candidates[0] != candidates[1] != candidates[2]
    for candidate in candidates:
        expand_schedule(candidate, contract)
