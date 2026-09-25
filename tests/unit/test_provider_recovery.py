import copy

import pytest
from google.genai.errors import ClientError
from httpx import ReadTimeout, Response

from agcws.core.storage import read, write
from agcws.search.providers import recovery as recovery

ARM = "strong-medium-64k"


@pytest.fixture
def setup(tmp_path, monkeypatch):
    root = tmp_path / "aes"
    root.mkdir()
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr(recovery.time, "sleep", lambda _: None)
    path = root / "panel/t/9100" / ARM / "batches/003"
    return root, path


def success():
    return {"raw_text": "malformed model output is still an output", "usage_unknown": False,
            "estimated_usd": .01, "api_error": None}


def test_retry_same_payload_and_account_each_attempt(setup, monkeypatch):
    root, path = setup
    calls = []

    def provider(*args):
        calls.append(copy.deepcopy(args))
        if len(calls) == 1:
            raise ClientError(429, {"error": {"status": "RESOURCE_EXHAUSTED"}})
        return success()

    monkeypatch.setattr(recovery, "generate", provider)
    meter = recovery.RecoveryMeter(root, 120)
    result = meter.call(path, ARM, "payload", {}, {"slot": 3})
    assert calls[0] == calls[1]
    assert result["raw_text"].startswith("malformed")
    assert meter.liability == pytest.approx(.39576 + .01)
    assert not (path / "trials.json").exists()
    assert recovery.RecoveryMeter(root, 120).call(path, ARM, "payload", {}, {"slot": 3}) == result
    assert len(calls) == 2
    with pytest.raises(ValueError, match="checkpoint differs"):
        meter.call(path, ARM, "changed", {}, {"slot": 3})


@pytest.mark.parametrize("error", [ReadTimeout("timeout"), ClientError(403, {"error": {"message": "denied"}})])
def test_ambiguous_or_permanent_error_pauses_every_design(setup, monkeypatch, error):
    root, path = setup
    calls = []

    def provider(*args):
        calls.append(args)
        raise error

    monkeypatch.setattr(recovery, "generate", provider)
    with pytest.raises(recovery.InfrastructurePause):
        recovery.RecoveryMeter(root, 120).call(path, ARM, "payload", {}, {})
    assert not (path / "response.json").exists()
    assert read(path / "attempts/001/response.json")["api_error"]
    other = root.parent / "dma"
    other.mkdir()
    with pytest.raises(recovery.InfrastructurePause):
        recovery.RecoveryMeter(other, 120).call(other / "batch", ARM, "payload", {}, {})
    assert len(calls) == 1


def test_exhaustion_does_not_emit_proposals(setup, monkeypatch):
    root, path = setup
    calls = []

    def provider(*args):
        calls.append(args)
        raise ClientError(429, {"error": {"status": "RESOURCE_EXHAUSTED"}})

    monkeypatch.setattr(recovery, "generate", provider)
    with pytest.raises(recovery.InfrastructurePause, match="retry limit"):
        recovery.RecoveryMeter(root, 120).call(path, ARM, "payload", {}, {})
    assert len(calls) == 4
    assert not (path / "response.json").exists()
    assert recovery.RecoveryMeter(root, 120).liability == pytest.approx(4 * .39576)


def test_cap_prevents_request(setup, monkeypatch):
    root, path = setup
    monkeypatch.setattr(recovery, "generate", lambda *a: pytest.fail("paid call"))
    with pytest.raises(recovery.InfrastructurePause, match="cost ceiling"):
        recovery.RecoveryMeter(root, 0).call(path, ARM, "payload", {}, {})
    assert not (path / "attempts/001/request_started.json").exists()


def test_unresolved_attempt_never_resampled(setup, monkeypatch):
    root, path = setup
    write(path / "attempts/001/request_started.json", {"reservation_usd": .39576})
    monkeypatch.setattr(recovery, "generate", lambda *a: pytest.fail("resampled unknown call"))
    with pytest.raises(recovery.InfrastructurePause, match="unresolved"):
        recovery.RecoveryMeter(root, 120).call(path, ARM, "payload", {}, {})


def test_explicit_billing_shutdown_does_not_retry(setup, monkeypatch):
    root, path = setup
    calls = []

    def provider(*args):
        calls.append(args)
        raise ClientError(429, {"error": {"details": [{"reason": "SPEND_CAP_EXCEEDED"}]}})

    monkeypatch.setattr(recovery, "generate", provider)
    with pytest.raises(recovery.InfrastructurePause, match="billing shutdown"):
        recovery.RecoveryMeter(root, 120).call(path, ARM, "payload", {}, {})
    assert len(calls) == 1


def test_recovery_launch_requires_authorization(tmp_path, monkeypatch):
    from agcws.studies import engine

    monkeypatch.setattr(engine, "verify_inputs", lambda *_: {"spec": {"policies": [ARM]}})
    with pytest.raises(ValueError, match="allow-paid"):
        engine.run(tmp_path, tmp_path)


def test_retry_after_and_request_identifier_preserved(setup, monkeypatch):
    root, path = setup
    calls = []
    delays = []
    monkeypatch.setattr(recovery.time, "sleep", delays.append)

    def provider(*args):
        calls.append(args)
        if len(calls) == 1:
            raise ClientError(429, {"error": {"status": "RESOURCE_EXHAUSTED"}},
                              Response(429, headers={"retry-after": "90", "x-request-id": "test-id"}))
        return success()

    monkeypatch.setattr(recovery, "generate", provider)
    recovery.RecoveryMeter(root, 120).call(path, ARM, "payload", {}, {})
    assert sum(delays) == 90
    assert max(delays) <= 30
    assert read(path / "attempts/001/response.json")["api_error"]["headers"]["x-request-id"] == "test-id"
