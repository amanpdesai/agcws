from types import SimpleNamespace

import pytest

from agcws.policies.structural import StructuralPopulationEvolution
from agcws.policies.structural_edit_agent import (
    StructuralPopulationAgent,
    StructuralPopulationHybrid,
)
from agcws.policies.structural_population import temporal_population


def trial(name, loss, rates, valid=True):
    return SimpleNamespace(workload={'name': name}, loss=loss,
                           validity=SimpleNamespace(valid=valid),
                           profile=SimpleNamespace(windowed=rates))


def test_population_preserves_other_peak_and_best_member():
    rows = [trial(str(i), i / 100, [10, 0]) for i in range(10)]
    other = trial('other', 0.9, [0, 10])
    rows += [other, trial('invalid', 0, [0, 10], False)]
    selected = temporal_population(rows)
    assert len(selected) == 8
    assert selected[0] is rows[0] and selected[1] is other
    assert rows[-1] not in selected
    assert rows[0].workload == {'name': '0'}


def test_duplicates_do_not_crowd_out_unique_schedules():
    rows = [trial('same', 0.1, [10, 0])] * 10 + [trial('new', 0.2, [10, 0])]
    assert len(temporal_population(rows)) == 2
    with pytest.raises(ValueError):
        temporal_population([trial('bad', float('nan'), [10, 0])])


def test_cpu_and_both_agents_share_parent_selection():
    rows = [trial(str(i), i / 100, [10, 0]) for i in range(10)] + [trial('other', 0.8, [0, 10])]
    cpu = StructuralPopulationEvolution(310)
    agent = StructuralPopulationAgent(lambda *_: '', 'prompt', model='test').initialize(310)
    hybrid = StructuralPopulationHybrid(lambda *_: '', 'prompt', model='test').initialize(310)
    assert cpu.select_parents(rows) == agent.select_parents(rows) == hybrid.select_parents(rows)
    assert isinstance(hybrid.evolution, StructuralPopulationEvolution)
