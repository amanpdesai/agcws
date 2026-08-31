from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.random_search import RandomSearch


def test_runner_counts_requested_slots_and_writes_curve(tmp_path):
    def evaluate(workload):
        return PowerProfile(5.0, 5.0, useful_work=16, valid=True)

    trials = run_search(AESAdapter(), RandomSearch(3), ScalarGoal(0.5), evaluate,
                        budget=5, batch_size=8, p_min=1, p_max=9, output_dir=tmp_path)
    assert len(trials) == 5
    assert len(__import__("json").loads((tmp_path / "best_so_far.json").read_text())["error"]) == 5
