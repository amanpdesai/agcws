from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from agcws.pipeline.meter import Meter
from agcws.pipeline.storage import read


def test_provider_calls_overlap_but_reservations_reconcile(tmp_path, monkeypatch):
    rendezvous = Barrier(2)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test-project")

    def generate(*args):
        rendezvous.wait(timeout=5)
        return {"raw_text": "{}", "usage_unknown": False, "estimated_usd": 0.01}

    monkeypatch.setattr("agcws.pipeline.meter.generate", generate)
    meter = Meter(tmp_path, 1, provider_workers=2)
    paths = [tmp_path / "panel/t/0/flash-4096/batches" / str(i) for i in range(2)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(meter.call, p, "flash-4096", "prompt", {}, {"slot": i})
                for i, p in enumerate(paths)]
        assert all(j.result()["estimated_usd"] == 0.01 for j in jobs)
    assert meter.liability == pytest.approx(0.02)
    assert Meter(tmp_path, 1).liability == pytest.approx(0.02)
    assert all(read(p / "request_started.json")["reservation_usd"] > 0 for p in paths)


def test_parallel_reservations_cannot_overspend(tmp_path, monkeypatch):
    from threading import Event

    started, release = Event(), Event()
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test-project")

    def generate(*args):
        started.set()
        assert release.wait(timeout=5)
        return {"raw_text": "{}", "usage_unknown": False, "estimated_usd": 0.01}

    monkeypatch.setattr("agcws.pipeline.meter.generate", generate)
    meter = Meter(tmp_path, 0.11, provider_workers=2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(meter.call, tmp_path / "first", "flash-4096", "p", {}, {})
        assert started.wait(timeout=5)
        try:
            with pytest.raises(RuntimeError, match="ceiling"):
                meter.call(tmp_path / "second", "flash-4096", "p", {}, {})
            assert not (tmp_path / "second/request_started.json").exists()
        finally:
            release.set()
        first.result()
    assert meter.liability == pytest.approx(0.01)


def test_server_failure_is_reserved_replayed_and_later_call_can_succeed(tmp_path, monkeypatch):
    from google.genai.errors import ServerError

    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test-project")
    calls = []

    def generate(*args):
        calls.append(args)
        if len(calls) == 1:
            raise ServerError(504, {"error": {"message": "injected deadline", "status": "DEADLINE_EXCEEDED"}})
        return {"raw_text": "{}", "usage_unknown": False, "estimated_usd": .01}

    monkeypatch.setattr("agcws.pipeline.meter.generate", generate)
    first = tmp_path / "panel/t/8502/flash-4096/batches/003"
    second = tmp_path / "panel/t/8502/flash-4096/batches/005"
    meter = Meter(tmp_path, 1)
    failed = meter.call(first, "flash-4096", "prompt", {}, {"slot": 3})
    reserved = read(first / "request_started.json")["reservation_usd"]
    assert failed["usage_unknown"] and failed["api_error"]["type"] == "ServerError"
    assert meter.liability == pytest.approx(reserved)
    resumed = Meter(tmp_path, 1)
    assert resumed.call(first, "flash-4096", "prompt", {}, {"slot": 3}) == failed
    assert len(calls) == 1  # No invisible resampling of the failed batch.
    assert resumed.call(second, "flash-4096", "prompt", {}, {"slot": 5})["estimated_usd"] == .01
    assert len(calls) == 2
    assert Meter(tmp_path, 1).liability == pytest.approx(reserved+.01)
