import copy
from types import SimpleNamespace

import pytest

from agcws.pipeline import model
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import write
from maintenance.prepare_flash_matrix import DESIGNS, matched
from maintenance.resume_budget import ReconciledMeter, reservation_bound
from maintenance.strong_matrix import ARM, execute
from tests.test_flash_matrix import pair


@pytest.mark.parametrize("design", DESIGNS)
def test_strong_contract(design):
    reference, candidate = pair(design)
    candidate["spec"]["policies"] = [ARM]
    candidate["models"] = {ARM: model.settings(ARM)}
    validate(candidate["spec"])
    assert matched(reference, candidate, ARM) == {}
    candidate["spec"]["tolerance"] = .02
    with pytest.raises(ValueError, match="task contract"):
        matched(reference, candidate, ARM)


def test_strong_transport_and_cost(monkeypatch):
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
                model_version="gemini-3.8-flash", prompt_feedback=None)

    monkeypatch.setattr(genai, "Client", Client)
    response = model.generate("fake", ARM, "history", {"type": "object"})
    assert calls[0]["model"] == "gemini-3.8-flash"
    assert calls[0]["config"]["thinking_config"] == {"thinking_level": "MEDIUM"}
    assert calls[0]["config"]["max_output_tokens"] == 8192
    assert "tools" not in calls[0]["config"]
    assert response["estimated_usd"] == pytest.approx(.0002625)
    assert model.settings("pro-4096")["model"] == "gemini-2.5-pro"


def test_strong_unknown_usage_and_resume(tmp_path, monkeypatch):
    from tests.test_budget_resume import unknown

    response = unknown()
    reserve = model.cost(ARM, 200000, 8192)
    assert reserve == pytest.approx(.18072)
    assert reservation_bound(response, reserve, ARM) == pytest.approx(.03372)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr("agcws.pipeline.meter.generate", lambda *args: copy.deepcopy(response))
    path = tmp_path / "panel/t/9100" / ARM / "batches/003"
    meter = ReconciledMeter(tmp_path, 120)
    meter.call(path, ARM, "history", {}, {})
    assert meter.liability == pytest.approx(.03372)
    assert ReconciledMeter(tmp_path, 120).liability == pytest.approx(.03372)


def test_launch_refuses_unapproved_or_changed_support(tmp_path):
    with pytest.raises(ValueError, match="allow-paid"):
        execute(tmp_path)
    write(tmp_path / "launch-contract.json", {"support_sha256": {}})
    with pytest.raises(ValueError, match="code changed"):
        execute(tmp_path, allow_paid=True)
