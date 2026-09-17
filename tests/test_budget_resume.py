import copy

import pytest

from agcws.pipeline.model import cost
from agcws.pipeline.provider_schema import provenance
from agcws.pipeline.storage import read, write
from maintenance.resume_budget import ReconciledMeter, reservation_bound

ARM = "flash-lite-medium"
RESERVED = cost(ARM, 200000, 8192)


def unknown():
    return {"usage_unknown": True, "estimated_usd": None,
            "usage_fields": {"prompt_token_count": 4000, "candidates_token_count": 300,
                             "thoughts_token_count": None}, "identity": {},
            "schema_provenance": provenance({}), "raw_text": "{}"}


def test_bound_keeps_full_output_budget():
    assert reservation_bound(unknown(), RESERVED, ARM) == pytest.approx(.02168)
    assert unknown()["usage_fields"]["thoughts_token_count"] is None


@pytest.mark.parametrize("change", [{"api_error": {"message": "504"}},
    {"usage_fields": {}}, {"usage_fields": {"prompt_token_count": -1}},
    {"usage_fields": {"prompt_token_count": 200001}},
    {"usage_fields": {"prompt_token_count": True}},
    {"usage_fields": {"prompt_token_count": 4000, "candidates_token_count": 99999}}])
def test_uncertain_input_keeps_original_reservation(change):
    response = {**unknown(), **change}
    assert reservation_bound(response, RESERVED, ARM) == RESERVED


def test_restart_replay_does_not_buy_again_or_double_settle(tmp_path, monkeypatch):
    directory = tmp_path / "panel/t/9100" / ARM / "batches/003"
    original = unknown()
    write(directory / "request_started.json", {"reservation_usd": RESERVED})
    write(directory / "response.json", original)
    monkeypatch.setattr("agcws.pipeline.meter.generate", lambda *args: pytest.fail("replayed API call"))
    meter = ReconciledMeter(tmp_path, 120)
    assert meter.liability == pytest.approx(.02168)
    assert meter.call(directory, ARM, "prompt", {}, {}) == original
    assert meter.liability == pytest.approx(.02168)
    assert ReconciledMeter(tmp_path, 120).liability == pytest.approx(.02168)
    assert read(directory / "response.json") == original


def test_new_response_adjusted_once_and_survives_restart(tmp_path, monkeypatch):
    directory = tmp_path / "panel/t/9100" / ARM / "batches/003"
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr("agcws.pipeline.meter.generate", lambda *args: copy.deepcopy(unknown()))
    meter = ReconciledMeter(tmp_path, 120)
    meter.call(directory, ARM, "prompt", {}, {})
    assert meter.liability == pytest.approx(.02168)
    assert ReconciledMeter(tmp_path, 120).liability == pytest.approx(.02168)


def test_unresolved_request_keeps_full_reservation_and_blocks_replay(tmp_path):
    directory = tmp_path / "panel/t/9100" / ARM / "batches/003"
    write(directory / "request_started.json", {"reservation_usd": RESERVED})
    meter = ReconciledMeter(tmp_path, 120)
    assert meter.liability == RESERVED
    with pytest.raises(RuntimeError, match="unresolved"):
        meter.call(directory, ARM, "prompt", {}, {})


def test_cap_still_blocks_a_new_call(tmp_path, monkeypatch):
    monkeypatch.setattr("agcws.pipeline.meter.generate", lambda *args: pytest.fail("over-budget call"))
    meter = ReconciledMeter(tmp_path, RESERVED / 2)
    directory = tmp_path / "panel/t/9100" / ARM / "batches/003"
    with pytest.raises(RuntimeError, match="ceiling"):
        meter.call(directory, ARM, "prompt", {}, {})
    assert not (directory / "request_started.json").exists()
