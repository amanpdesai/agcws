"""Real spawned workers retain cell checkpoints without inheriting parent locks."""

import json
import multiprocessing
import os
import pickle
from concurrent.futures import ProcessPoolExecutor

import pytest

from agcws.evaluation.power import panel
from agcws.reporting.metrics import key
from agcws.studies import power_queue

_barrier = None


def fake_measurement(plan, case_id, synthesis, out, **kwargs):
    _barrier.wait(timeout=15)
    if case_id == 'bad':
        raise ValueError('intentional invalid fixture')
    out.mkdir()
    (out / 'measurement.json').write_text(json.dumps(
        {'case_id': case_id, 'plan_sha256': plan['sha256'], 'fixture': 42}))


def initialize_test_worker(collections, barrier):
    global _barrier
    _barrier = barrier
    panel.run = fake_measurement
    power_queue.initialize_worker(collections)


def test_spawn_parallel_resume_failure_and_lock_owner(tmp_path):
    synthesis = tmp_path / 'synthesis'
    synthesis.mkdir()
    (synthesis / 'manifest.json').write_text('{}')
    body = {'inputs': {}, 'cases': [{'id': name, 'domain': 'aes-temporal'}
                                   for name in ['one', 'two', 'bad', 'four']], 'omitted': []}
    plan = {**body, 'sha256': key(body)}
    mapping = {'aes-temporal': synthesis}
    ctx = multiprocessing.get_context('spawn')
    with panel.Collection(plan, mapping, tmp_path / 'out') as collection:
        assert 'lock' not in pickle.loads(pickle.dumps(collection)).__dict__
        with ProcessPoolExecutor(max_workers=2, mp_context=ctx,
                                 initializer=initialize_test_worker,
                                 initargs=({'fixture': collection}, ctx.Barrier(2))) as pool:
            futures = [pool.submit(power_queue.run_case, 'fixture', case) for case in plan['cases']]
            results = [future.result(timeout=30) for future in futures]
            assert len({r['worker_pid'] for r in results}) == 2
            assert all(r['worker_pid'] != os.getpid() for r in results)
            assert [r['status'] for r in results] == ['measured', 'measured', 'failed', 'measured']
            # A competing coordinator cannot enter while workers are active.
            with pytest.raises(BlockingIOError), panel.Collection(plan, mapping, tmp_path / 'out'):
                pass
            retained = pool.submit(power_queue.run_case, 'fixture', plan['cases'][0]).result(timeout=10)
            assert retained['status'] == 'retained'
    with panel.Collection(plan, mapping, tmp_path / 'out') as resumed:
        assert resumed.retained(plan['cases'][0])['status'] == 'retained'
        assert resumed.retained(plan['cases'][2]) is None
    assert len(list((tmp_path / 'out/one').glob('attempt-*'))) == 1
    assert (tmp_path / 'out/bad/attempt-001/failure.json').is_file()
