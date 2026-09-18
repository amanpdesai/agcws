import copy
import multiprocessing
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from agcws.pipeline import model
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import write
from maintenance.prepare_flash_matrix import DESIGNS, matched
from maintenance.resume_budget import ReconciledMeter, reservation_bound
from maintenance.strong_matrix import ARM, StrongMeter, execute
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
    assert calls[0]["config"]["max_output_tokens"] == 65536
    assert "tools" not in calls[0]["config"]
    assert response["estimated_usd"] == pytest.approx(.0002625)
    assert model.settings("pro-4096")["model"] == "gemini-2.5-pro"


def test_strong_unknown_usage_and_resume(tmp_path, monkeypatch):
    from tests.test_budget_resume import unknown

    response = unknown()
    reserve = model.cost(ARM, 200000, 65536)
    assert reserve == pytest.approx(.39576)
    assert reservation_bound(response, reserve, ARM) == pytest.approx(.24876)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr("agcws.pipeline.meter.generate", lambda *args: copy.deepcopy(response))
    path = tmp_path / "panel/t/9100" / ARM / "batches/003"
    meter = ReconciledMeter(tmp_path, 120)
    meter.call(path, ARM, "history", {}, {})
    assert meter.liability == pytest.approx(.24876)
    assert ReconciledMeter(tmp_path, 120).liability == pytest.approx(.24876)


def test_launch_refuses_unapproved_or_changed_support(tmp_path):
    with pytest.raises(ValueError, match="allow-paid"):
        execute(tmp_path)
    write(tmp_path / "launch-contract.json", {"support_sha256": {}})
    with pytest.raises(ValueError, match="code changed"):
        execute(tmp_path, allow_paid=True)


def _admission_child(root, events):
    def provider(self, *args):
        events.put(("enter", str(root), time.monotonic()))
        time.sleep(.03)
        events.put(("exit", str(root), time.monotonic()))
        return {}

    ReconciledMeter.call = provider
    StrongMeter(root, 2).call(root / "batch", ARM, "payload", {}, {})


def test_provider_admission_serializes_design_processes(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    events = ctx.Queue()
    roots = [tmp_path / name for name in ("aes", "ibex", "mesh")]
    for root in roots:
        root.mkdir()
    jobs = [ctx.Process(target=_admission_child, args=(root, events)) for root in roots]
    for job in jobs:
        job.start()
    try:
        records = [events.get(timeout=20) for _ in range(6)]
        for job in jobs:
            job.join(timeout=20)
            assert job.exitcode == 0
    finally:
        for job in jobs:
            if job.is_alive():
                job.terminate()
                job.join()
        events.close()
    records.sort(key=lambda item: item[2])
    assert [r[0] for r in records] == ["enter", "exit"] * 3
    assert all((Path(root) / "batch/admission.json").exists() for root in roots)


def test_provider_admission_releases_after_exception(tmp_path, monkeypatch):
    root = tmp_path / "aes"
    root.mkdir()
    meter = StrongMeter(root, 2)

    def failure(*args):
        raise RuntimeError("test failure")

    monkeypatch.setattr(ReconciledMeter, "call", failure)
    with pytest.raises(RuntimeError, match="test failure"):
        meter.call(root / "first", ARM, "payload", {}, {})
    monkeypatch.setattr(ReconciledMeter, "call", lambda *args: {"recovered": True})
    assert meter.call(root / "second", ARM, "payload", {}, {}) == {"recovered": True}
