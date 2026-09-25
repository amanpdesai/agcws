import json
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import pytest

from agcws.evaluation.power import panel
from agcws.reporting.metrics import key
from agcws.studies import power_queue


@pytest.fixture(autouse=True)
def inline_test_workers(monkeypatch):
    # Scheduler unit tests keep their local fakes and thread barriers. Real spawn
    # and lock ownership are exercised separately in test_power_processes.py.
    def pool(*, mp_context, **kwargs):
        assert mp_context.get_start_method() == 'spawn'
        return ThreadPoolExecutor(**kwargs)
    monkeypatch.setattr(power_queue, 'ProcessPoolExecutor', pool)


def prepare(tmp_path, monkeypatch, sizes=(1, 5)):
    synthesis = tmp_path / 'synthesis'
    synthesis.mkdir()
    (synthesis / 'manifest.json').write_text('{}')
    entries, calls = [], []
    for i, size in enumerate(sizes):
        body = {'inputs': {}, 'cases': [{'id': f'{i}-{j}', 'domain': 'aes-temporal'}
                                       for j in range(size)], 'omitted': []}
        plan = tmp_path / f'plan-{i}.json'
        plan.write_text(json.dumps({**body, 'sha256': key(body)}))
        entries.append({'name': str(i), 'plan': str(plan), 'out': str(tmp_path / str(i))})

    def run(plan, case_id, synthesis, out, **kwargs):
        calls.append(case_id)
        out.mkdir()
        (out / 'measurement.json').write_text(json.dumps(
            {'case_id': case_id, 'plan_sha256': plan['sha256']}))

    monkeypatch.setattr(panel, 'run', run)
    return entries, {'aes-temporal': synthesis}, calls


def test_largest_backlog_gets_released_workers():
    buckets = {'finished': {'pending': deque(), 'active': 0, 'ready': True},
               'small': {'pending': deque([1]), 'active': 1, 'ready': True},
               'large': {'pending': deque(range(8)), 'active': 2, 'ready': True}}
    assert power_queue.select_bucket(buckets) == 'large'
    buckets['large']['pending'].clear()
    assert power_queue.select_bucket(buckets) == 'small'


def test_idle_bucket_receives_a_worker_before_backlog_expansion():
    buckets = {'small': {'pending': deque([1]), 'active': 0, 'ready': True},
               'large': {'pending': deque(range(80)), 'active': 20, 'ready': True}}
    assert power_queue.select_bucket(buckets) == 'small'


def test_global_limit_and_worker_reassignment(tmp_path, monkeypatch):
    entries, mapping, calls = prepare(tmp_path, monkeypatch, (1, 7))
    original = panel.run
    barrier = threading.Barrier(2)
    lock = threading.Lock()
    active = peak = 0

    def run(*args, **kwargs):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        # Both first-case checks overlap. Once bucket 0 finishes, bucket 1
        # must use both workers; otherwise this barrier cannot be satisfied.
        barrier.wait(timeout=5)
        original(*args, **kwargs)
        with lock:
            active -= 1

    monkeypatch.setattr(panel, 'run', run)
    result = power_queue.collect_many(entries, mapping, workers=2)
    assert all(r['all_passed'] for r in result.values())
    assert peak == 2 and len(calls) == 8
    power_queue.collect_many(entries, mapping, workers=2)
    assert len(calls) == 8


def test_failed_preflight_does_not_block_other_bucket(tmp_path, monkeypatch):
    entries, mapping, calls = prepare(tmp_path, monkeypatch, (3, 4))
    original = panel.run

    def run(plan, case_id, *args, **kwargs):
        if case_id == '0-0':
            raise ValueError('bad replay')
        return original(plan, case_id, *args, **kwargs)

    monkeypatch.setattr(panel, 'run', run)
    result = power_queue.collect_many(entries, mapping, workers=2)
    assert not result['0']['all_passed'] and result['1']['all_passed']
    assert [c['status'] for c in result['0']['cases']] == ['failed', 'deferred', 'deferred']
    assert len(calls) == 4


def test_drain_preserves_completed_and_resumes(tmp_path, monkeypatch):
    entries, mapping, calls = prepare(tmp_path, monkeypatch)
    result = power_queue.collect_many(entries, mapping, workers=1, stop=lambda: len(calls) >= 2)
    assert len(calls) == 2
    assert not all(r['all_passed'] for r in result.values())
    result = power_queue.collect_many(entries, mapping, workers=2)
    assert all(r['all_passed'] for r in result.values())
    assert len(calls) == len(set(calls)) == 6


def test_amendment_only_permits_exact_orchestrator_change(tmp_path, monkeypatch):
    entries, mapping, calls = prepare(tmp_path, monkeypatch)
    power_queue.collect_many(entries, mapping, workers=2)
    name = 'src/agcws/evaluation/power/panel.py'
    path = tmp_path / '0/collection.json'
    identity = json.loads(path.read_text())
    after = identity['validation_sources'][name]
    identity['validation_sources'][name] = 'old-panel-sha'
    path.write_text(json.dumps(identity))
    amendment = {'panel': {'before': 'old-panel-sha', 'after': after}}
    result = power_queue.collect_many(entries, mapping, workers=2, amendment=amendment)
    assert result['0']['all_passed'] and len(calls) == 6
    assert json.loads(path.read_text()) == identity
    amendment_path = tmp_path / 'amendment.json'
    amendment_path.write_text(json.dumps(amendment))
    entries[0]['amendment'] = str(amendment_path)
    assert power_queue.collect_many(entries, mapping, workers=2)['0']['all_passed']
    identity['minimum_coverage'] = .5
    path.write_text(json.dumps(identity))
    with pytest.raises(ValueError, match='measurement identity'):
        power_queue.collect_many(entries, mapping, workers=2, amendment=amendment)


def test_duplicate_output_rejected(tmp_path, monkeypatch):
    entries, mapping, calls = prepare(tmp_path, monkeypatch)
    entries[1]['out'] = entries[0]['out']
    with pytest.raises(ValueError, match='duplicate collection'):
        power_queue.collect_many(entries, mapping, workers=2)
