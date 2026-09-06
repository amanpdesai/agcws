import json
from types import SimpleNamespace

from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.adapters.base import Validity
from agcws.experiments.runner import run_search
from agcws.goals.schema import FixedTemporalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.structural import StructuralRandom
from agcws.policies.structural_agent import StructuralAgent, StructuralHybrid
from agcws.workloads.schedule import ScheduleContract


def setup():
    adapter = AESTemporalAdapter(ScheduleContract(64, 6000))
    goal = FixedTemporalGoal(windows=2, profile=[0, 100], scale=200, observation_cycles=6774)
    schedule = {'sequence': [{'op': 'work', 'units': 64}, {'op': 'wait', 'cycles': 6000}]}
    profile = PowerProfile(0, 0, windowed=[0, 100], useful_work=64, valid=True,
                           provenance={'clock_edges': 6774})
    return adapter, goal, schedule, profile


def test_agent_payload_has_contract_vector_feedback_and_no_reference_solution():
    adapter, goal, schedule, profile = setup()
    policy = StructuralAgent(lambda *_: '[]', 'prompt', model='test').initialize(310)
    history = [SimpleNamespace(workload=schedule, profile=profile, loss=0.0,
                               validity=Validity(True))]
    payload = json.loads(policy.build_payload(adapter, goal, history, 4, 'prompt'))
    assert payload['contract']['work_units'] == 64
    assert payload['history'][0]['signed_residual'] == [0, 0]
    assert payload['schema'] == adapter.workload_schema
    assert 'reference' not in payload
    assert policy.propose(adapter, goal, [], 4) == StructuralRandom(310).propose(adapter, goal, [], 4)


def test_short_batch_charges_missing_slots_and_cost_once(tmp_path, monkeypatch):
    adapter, goal, schedule, profile = setup()
    calls = []
    monkeypatch.setenv('AGCWS_GEMINI_INPUT_USD_PER_MILLION', '1')
    monkeypatch.setenv('AGCWS_GEMINI_OUTPUT_USD_PER_MILLION', '2')

    def generate(*args):
        calls.append(args)
        return json.dumps([schedule]), {'tokens_in': 100, 'tokens_out': 20}

    policy = StructuralAgent(generate, 'prompt', model='test').initialize(310)
    trials = run_search(adapter, policy, goal, lambda _: profile,
                        budget=8, batch_size=4, seed=310, output_dir=tmp_path)
    assert len(calls) == 1 and len(trials) == 8
    assert sum(t.validity.valid for t in trials) == 5
    assert sum(t.tokens_in for t in trials) == 100
    assert sum(t.tokens_out for t in trials) == 20
    assert sum(t.est_cost_usd for t in trials) == 0.00014


def test_hybrid_alternates_and_does_not_repeat_usage_on_cpu_batch():
    adapter, goal, schedule, profile = setup()
    calls = []

    def generate(*_):
        calls.append(1)
        return json.dumps([schedule] * 4), {'tokens_in': 100, 'tokens_out': 20}

    policy = StructuralHybrid(generate, 'prompt', model='test').initialize(310)
    trials = run_search(adapter, policy, goal, lambda _: profile,
                        budget=16, batch_size=4, seed=310)
    assert len(calls) == 2
    assert sum(t.tokens_in for t in trials) == 200
    assert trials[8].generation_diagnostics['proposal_source'] == 'structural_evolution'


def test_malformed_batch_does_not_get_free_repair():
    adapter, goal, _, profile = setup()
    calls = []

    def generate(*_):
        calls.append(1)
        return 'not json', {'tokens_in': 100, 'tokens_out': 20}

    policy = StructuralAgent(generate, 'prompt', model='test').initialize(310)
    trials = run_search(adapter, policy, goal, lambda _: profile, budget=8, batch_size=4)
    assert len(calls) == 1 and sum(t.validity.valid for t in trials) == 4
    assert sum(t.tokens_in for t in trials) == 100
