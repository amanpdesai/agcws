import json
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import ScalarGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.agent import AgentPolicy
from agcws.policies.agent import OfflineAgent
from agcws.policies.vertex import VertexAgent


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
    assert trials[0].claim_scope == "cross_design_agent"


def test_policy_claim_scopes_are_explicit():
    assert OfflineAgent().claim_scope == "heuristic_smoke_only"
    assert VertexAgent(lambda *_: "[]", "system", model="test").claim_scope == "cross_design_agent"


def test_runner_records_batch_usage_once(tmp_path: Path):
    policy = AgentPolicy(lambda *_: [{"operations": []}, {"operations": []}],
                         model="test-model", prompt_hash="abc123")
    policy.last_usage = {"tokens_in": 20, "tokens_out": 9}

    trials = run_search(AESAdapter(), policy, ScalarGoal(0.5),
                        lambda _: PowerProfile(2.0, 2.0, useful_work=21, valid=True),
                        budget=2, batch_size=2, p_min=1.0, p_max=3.0,
                        output_dir=tmp_path)
    assert [(trial.tokens_in, trial.tokens_out) for trial in trials] == [(20, 9), (0, 0)]
    archived = [json.loads(line) for line in (tmp_path / "trials.jsonl").read_text().splitlines()]
    assert sum(item["tokens_in"] for item in archived) == 20
    assert sum(item["tokens_out"] for item in archived) == 9
