"""Concurrent cells share recovery admission and durable reservations."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from agcws.core.storage import read
from agcws.search.providers import recovery


def test_parallel_cells_serialize_provider_and_reconcile_reservations(tmp_path, monkeypatch):
    tmp_path = tmp_path / "study"
    tmp_path.mkdir()
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test-project")
    active = 0
    peak = 0
    count_lock = threading.Lock()

    def generate(*args):
        nonlocal active, peak
        with count_lock:
            active += 1
            peak = max(peak, active)
        time.sleep(.01)
        with count_lock:
            active -= 1
        return {"raw_text": "{}", "usage_unknown": False, "estimated_usd": .01}

    monkeypatch.setattr(recovery, "generate", generate)
    meter = recovery.RecoveryMeter(tmp_path, 1, provider_workers=2)
    paths = [tmp_path / "panel/t/0/flash-4096/batches" / str(i) for i in range(2)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(meter.call, p, "flash-4096", "prompt", {}, {"slot": i})
                for i, p in enumerate(paths)]
        assert all(j.result()["estimated_usd"] == .01 for j in jobs)
    assert peak == 1
    assert recovery.RecoveryMeter(tmp_path, 1).liability == pytest.approx(.02)
    assert all(read(p / "attempts/001/request_started.json")["reservation_usd"] > 0 for p in paths)


def test_concurrent_waiters_observe_global_pause(tmp_path, monkeypatch):
    tmp_path = tmp_path / "study"
    tmp_path.mkdir()
    monkeypatch.setattr(recovery, "generate", lambda *args: pytest.fail("unexpected call"))
    meter = recovery.RecoveryMeter(tmp_path, 0)
    paths = [tmp_path / "panel/t/0/flash-4096/batches" / str(i) for i in range(2)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(meter.call, p, "flash-4096", "prompt", {}, {}) for p in paths]
        for job in jobs:
            with pytest.raises(recovery.InfrastructurePause):
                job.result()
    assert not list(tmp_path.rglob("request_started.json"))
