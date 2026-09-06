import json

from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import FixedTemporalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.structural_edit_agent import (
    StructuralEditAgent,
    StructuralEditHybrid,
)
from agcws.workloads.schedule import ScheduleContract, expand_schedule


def run(policy_class, generate):
    adapter = AESTemporalAdapter(ScheduleContract(64, 6000))
    goal = FixedTemporalGoal(windows=2, profile=[0, 100], scale=200, observation_cycles=6774)
    profile = PowerProfile(0, 0, windowed=[0, 100], valid=True, useful_work=64,
                           provenance={'clock_edges': 6774})
    policy = policy_class(generate, 'prompt', model='test').initialize(310)
    return run_search(adapter, policy, goal, lambda _: profile, budget=16, batch_size=4)


def test_typed_edits_use_listed_parent_and_preserve_budgets():
    calls = []

    def generate(_, text):
        payload = json.loads(text)
        calls.append(payload)
        parent = payload['parents'][0]
        assert parent['sequence'][0]['index'] == 0
        return json.dumps([{'parent_id': parent['parent_id'],
                            'edit': {'op': 'swap', 'a': 0, 'b': 1}}] * 4), {'tokens_in': 100, 'tokens_out': 20}

    trials = run(StructuralEditAgent, generate)
    assert len(calls) == 3 and all(t.validity.valid for t in trials)
    assert sum(t.tokens_in for t in trials) == 300
    for trial in trials:
        assert expand_schedule(trial.workload, ScheduleContract(64, 6000))


def test_bad_parent_charged_once_with_actionable_feedback():
    calls = []

    def generate(_, text):
        calls.append(json.loads(text))
        return json.dumps([{'parent_id': 'not_a_parent', 'edit': {'op': 'swap', 'a': 0, 'b': 1}}] * 4)

    trials = run(StructuralEditAgent, generate)
    assert len(calls) == 3 and sum(t.validity.valid for t in trials) == 4
    assert 'not_a_parent' in calls[1]['recent_feedback'][-1]['rejection']
    assert len(trials[4].generation_diagnostics['structural_edit_failures']) == 4


def test_hybrid_cpu_batches_are_not_reinterpreted_as_model_edits():
    calls = []

    def generate(_, text):
        calls.append(1)
        parent = json.loads(text)['parents'][0]
        return json.dumps([{'parent_id': parent['parent_id'],
                            'edit': {'op': 'move', 'a': 0, 'b': 1}}] * 4), {'tokens_in': 100, 'tokens_out': 20}

    trials = run(StructuralEditHybrid, generate)
    assert len(calls) == 2 and all(t.validity.valid for t in trials)
    assert sum(t.tokens_in for t in trials) == 200
    assert trials[8].generation_diagnostics['proposal_source'] == 'structural_evolution'
