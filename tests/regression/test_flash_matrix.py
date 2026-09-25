import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agcws.evidence.flash_contract import ARM, DESIGNS, matched
from agcws.search.dispatch import Policy
from agcws.search.providers import gemini as model
from agcws.studies.spec import validate


def pair(design="aes"):
    reference = json.loads(Path(f"results/{design}/tasks/plan/manifest.json").read_text())
    candidate = copy.deepcopy(reference)
    candidate["spec"].update(name="matched", policies=[ARM], cost_ceiling_usd=120)
    candidate["models"] = {ARM: model.settings(ARM)}
    return reference, candidate


@pytest.mark.parametrize("design", DESIGNS)
def test_all_designs_accept_matched_arm(design):
    reference, candidate = pair(design)
    validate(candidate["spec"])
    assert matched(reference, candidate) == {}


@pytest.mark.parametrize("design", DESIGNS)
def test_published_manifests_keep_original_source_identities(design):
    reference, _ = pair(design)
    candidate = json.loads(Path(
        f"results/{design}/tasks/flash_plan/manifest.json"
    ).read_text())
    changes = matched(reference, candidate)
    assert set(changes) == {"src/agcws/pipeline/model.py",
                            "src/agcws/pipeline/schedule_backend.py"}


@pytest.mark.parametrize("design", DESIGNS)
def test_shared_initializations_identical(design, tmp_path):
    reference, candidate = pair(design)
    spec = candidate["spec"]
    target = next(iter(spec["targets"].values()))
    for seed in spec["seeds"]:
        common = dict(spec=spec, target=target, schema=candidate["schema"], meter=None)
        baseline = Policy("phase-random", seed, **common).propose([], tmp_path, {})
        agent = Policy(ARM, seed, **common).propose([], tmp_path, {})
        assert baseline == agent


@pytest.mark.parametrize("field,value", [("seeds", [999]), ("tolerance", .1),
                                         ("success_metric", "nrmse"), ("budget", 16)])
def test_contract_drift_rejected(field, value):
    reference, candidate = pair()
    candidate["spec"][field] = value
    with pytest.raises(ValueError, match="task contract"):
        matched(reference, candidate)


def test_evaluator_drift_rejected():
    reference, candidate = pair()
    candidate["sources"]["src/agcws/reporting/metrics.py"] = "changed"
    with pytest.raises(ValueError, match="non-provider"):
        matched(reference, candidate)


def test_provider_request_has_no_tools_or_budget_alias(monkeypatch):
    from google import genai

    calls = []

    class Client:
        def __init__(self, **kwargs):
            self.models = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(usage_metadata=SimpleNamespace(prompt_token_count=100,
                candidates_token_count=20, thoughts_token_count=30), candidates=[],
                model_version="gemini-3.5-flash-lite", prompt_feedback=None)

    monkeypatch.setattr(genai, "Client", Client)
    result = model.generate("fake-project", ARM, "measured history", {"type": "object"})
    assert calls[0]["model"] == "gemini-3.5-flash-lite"
    assert calls[0]["config"]["thinking_config"] == {"thinking_level": "MEDIUM"}
    assert "tools" not in calls[0]["config"]
    assert calls[0]["config"]["max_output_tokens"] == 8192
    assert result["estimated_usd"] == pytest.approx(.000155)
    assert model.settings("flash-4096")["thinking_budget"] == 4096
