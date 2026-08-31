from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.agent import AgentPolicy


def test_runner_records_agent_metadata(tmp_path: Path):
    policy = AgentPolicy(lambda *_: [{"operations": [{"op": "configure"},
                                                       {"op": "encrypt", "blocks": 16}]}],
                         model="test-model", prompt_hash="abc123")

    def evaluate(_):
        return PowerProfile(mean_power=2.0, peak_power=2.0, useful_work=16, valid=True)

    trials = run_search(AESAdapter(), policy, ScalarGoal(0.5), evaluate,
                        budget=1, p_min=1.0, p_max=3.0, output_dir=tmp_path)
    assert trials[0].model == "test-model"
    assert trials[0].prompt_hash == "abc123"
