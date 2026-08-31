from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch
from agcws.policies.agent import AgentPolicy


def test_runner_counts_requested_slots_and_writes_curve(tmp_path):
    def evaluate(workload):
        return PowerProfile(5.0, 5.0, useful_work=16, valid=True)

    trials = run_search(AESAdapter(), RandomSearch(3), ScalarGoal(0.5), evaluate,
                        budget=5, batch_size=8, p_min=1, p_max=9, output_dir=tmp_path)
    assert len(trials) == 5
    assert len(__import__("json").loads((tmp_path / "best_so_far.json").read_text())["error"]) == 5


def test_runner_applies_runtime_useful_work_gate():
    def evaluate(workload):
        return PowerProfile(5.0, 5.0, useful_work=1, valid=True)

    trials = run_search(AESAdapter(), RandomSearch(3), ScalarGoal(0.5), evaluate,
                        budget=1, p_min=1, p_max=9)
    assert not trials[0].validity.valid
    assert trials[0].validity.stage.value == "USEFUL_WORK"
    assert trials[0].profile is not None
    assert trials[0].loss is None


def test_runner_records_malformed_batch_as_consumed_schema_slots():
    policy = AgentPolicy(lambda *_: (_ for _ in ()).throw(ValueError("bad JSON")))
    calls = []

    def evaluate(workload):
        calls.append(workload)
        return PowerProfile(1.0, 1.0, useful_work=24, valid=True)

    trials = run_search(AESAdapter(), policy, ScalarGoal(0.5), evaluate,
                        budget=3, batch_size=3, p_min=0.0, p_max=2.0)
    assert len(trials) == 3
    assert not calls
    assert all(trial.validity.stage.value == "SCHEMA" for trial in trials)
