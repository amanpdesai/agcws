"""Share replay workers across collections, prioritizing the largest backlog."""

import argparse
import json
import multiprocessing
import os
import signal
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from contextlib import ExitStack
from pathlib import Path

from agcws.core.storage import read, write
from agcws.evaluation.power.panel import Collection

_collections = {}


def initialize_worker(collections):
    global _collections
    _collections = collections


def run_case(name, case):
    result = _collections[name].cell(case)
    return {**result, 'worker_pid': os.getpid()}


def select_bucket(buckets):
    eligible = [name for name, b in buckets.items()
                if b['pending'] and (b['ready'] or not b['active'])]
    if not eligible:
        return None
    # Admit each readiness case before scaling any one collection.
    fresh = [name for name in eligible if not buckets[name]['ready']]
    idle = [name for name in eligible if not buckets[name]['active']]
    candidates = fresh or idle or eligible
    return min(candidates, key=lambda name: (
        -len(buckets[name]['pending']),
        buckets[name]['active'], name))


def collect_many(entries, syntheses, *, workers, amendment=None, stop=None):
    if workers < 1:
        raise ValueError('workers must be positive')
    names = [entry['name'] for entry in entries]
    outputs = [str(Path(entry['out']).resolve()) for entry in entries]
    if len(set(names)) != len(names) or len(set(outputs)) != len(outputs):
        raise ValueError('duplicate collection name or output')
    stop = stop or (lambda: False)
    with ExitStack() as stack:
        buckets = {}
        for entry in entries:
            collection = stack.enter_context(Collection(
                read(Path(entry['plan'])), {**syntheses, **entry.get('additional_syntheses', {})},
                Path(entry['out']),
                runtime=Path(entry['runtime']) if entry.get('runtime') else None,
                amendment=read(Path(entry['amendment'])) if entry.get('amendment') else amendment))
            results, pending = [], deque()
            ids = [c['id'] for c in collection.plan['cases']]
            if len(set(ids)) != len(ids):
                raise ValueError('duplicate case identity')
            first_retained = not ids
            for i, case in enumerate(collection.plan['cases']):
                retained = collection.retained(case)
                if retained:
                    results.append(retained)
                    if i == 0:
                        first_retained = True
                else:
                    pending.append(case)
            buckets[entry['name']] = dict(collection=collection, pending=pending,
                                          results=results, ready=first_retained, active=0)
            print(json.dumps({'bucket': entry['name'], 'retained': len(results),
                              'pending': len(pending)}), flush=True)

        with ProcessPoolExecutor(
            max_workers=workers, mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize_worker,
            initargs=({name: b['collection'] for name, b in buckets.items()},),
        ) as pool:
            futures = {}
            while futures or any(b['pending'] for b in buckets.values()):
                while len(futures) < workers and not stop():
                    name = select_bucket(buckets)
                    if name is None:
                        break
                    bucket = buckets[name]
                    case = bucket['pending'].popleft()
                    bucket['active'] += 1
                    futures[pool.submit(run_case, name, case)] = name
                if not futures:
                    break
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    name = futures.pop(future)
                    bucket = buckets[name]
                    result = future.result()
                    bucket['active'] -= 1
                    bucket['results'].append(result)
                    if not bucket['ready']:
                        if result['status'] == 'failed':
                            bucket['results'].extend(
                                {'case': c['id'], 'status': 'deferred',
                                 'error': 'First-case readiness replay failed'}
                                for c in bucket['pending'])
                            bucket['pending'].clear()
                        else:
                            bucket['ready'] = True
                    event = {'bucket': name, 'completed': len(bucket['results']),
                             'total': len(bucket['collection'].plan['cases']),
                             'active': bucket['active'], **result}
                    print(json.dumps(event), flush=True)

        reports = {}
        for name, bucket in buckets.items():
            bucket['results'].extend({'case': c['id'], 'status': 'deferred',
                                      'error': 'Operator requested drain'}
                                     for c in bucket['pending'])
            reports[name] = bucket['collection'].finish(bucket['results'], preflight=True)
        return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collections', required=True, type=Path)
    parser.add_argument('--syntheses', required=True, type=Path)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--amendment', type=Path)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    draining = False

    def drain(signum, frame):
        nonlocal draining
        draining = True
        print(json.dumps({'draining': True, 'signal': signum}), flush=True)

    signal.signal(signal.SIGTERM, drain)
    signal.signal(signal.SIGINT, drain)
    reports = collect_many(read(args.collections), read(args.syntheses), workers=args.workers,
                           amendment=read(args.amendment) if args.amendment else None,
                           stop=lambda: draining)
    passed = all(r['all_passed'] for r in reports.values())
    write(args.receipt, {'all_passed': passed, 'workers': args.workers,
                         'executor': 'spawn-process-pool',
                         'collections': {name: {'all_passed': r['all_passed'],
                                               'cases': len(r['cases'])}
                                         for name, r in reports.items()}})
    if not passed:
        raise SystemExit('Power queue retained failed or deferred cases; inspect reports')


if __name__ == '__main__':
    main()
