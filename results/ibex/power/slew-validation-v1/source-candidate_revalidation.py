"""Resumable, power-only Ibex candidate revalidation from authoritative archives."""

import argparse
import concurrent.futures
import copy
import fcntl
import gzip
import hashlib
import json
import multiprocessing
import os
import time
from collections import Counter
from pathlib import Path

from agcws.evaluation.power.reconstruction_audit import POLICY, audit_archived
from agcws.evaluation.power.windows import reconstruction
from agcws.evidence import catalog
from agcws.evidence.retention import file_digest
from agcws.reporting.power_reference import compare_measurements

VERSION = 'ibex-candidate-slew-revalidation-v1'
ARMS = ('phase-random', 'phase-ga', 'phase-model', 'flash-lite-medium', 'strong-medium-64k')


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    """Atomic, durable progress/artifact publication within the new batch root."""
    path = Path(path)
    pending = path.with_suffix(path.suffix + '.pending')
    with pending.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    pending.replace(path)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    if file_digest(Path(path))[0] != expected:
        raise ValueError(f'changed source: {path}')


def native_setup(power):
    inputs = power['inputs']
    def one(suffix):
        values = [v for k, v in inputs.items() if k.endswith(suffix)]
        if len(values) != 1:
            raise ValueError(f'ambiguous setup identity: {suffix}')
        return values[0]
    return {'scope': power['scope'], 'clock_period_s': power['clock_period_s'],
            'tool_version': power['tool_version'], 'tool_sha256': one('/sta'),
            'netlist_sha256': one('/mapped.v'), 'liberty_sha256': one('.lib'),
            'durations_s': power['grid']['durations_s']}


def revised_measurement(original, receipt, receipt_path):
    """Keep the entire activity and native numerical record; replace only evidence."""
    if (receipt['native_power'] != original['power']
            or receipt['source_inputs'] != original['power']['inputs']
            or receipt['target'] != original['activity']['target']):
        raise ValueError('audit receipt is for a different measurement/setup')
    source = Path(receipt['measurement'])
    checked(source, receipt['measurement_sha256'])
    if read(source) != original:
        raise ValueError('audit source measurement differs')
    diagnostic = receipt['switching_reconstruction']
    power = original['power']
    values = [r['leaf_switching_sum_w'] for r in power['windows']]
    verified = reconstruction(power['full']['leaf_switching_sum_w'],
                              power['weighted_leaf_switching_w'], policy=POLICY,
                              top='ibex_top', period_s=power['clock_period_s'],
                              proof=diagnostic.get('proof'), window_values=values,
                              durations_s=power['grid']['durations_s'])
    if not verified['accepted_estimate']:
        raise ValueError('failed or incomplete candidate proof')
    artifacts = receipt['artifact_sha256']
    for name, expected in artifacts.items():
        if Path(name).name != name:
            raise ValueError('unsafe evidence filename')
        checked(receipt_path.parent / name, expected)
    for name, expected in verified['proof']['report_sha256'].items():
        path = Path(name)
        if path.resolve().parent != receipt_path.parent.resolve():
            raise ValueError('proof report outside candidate audit')
        checked(path, expected)
        if artifacts.get(path.name) != expected:
            raise ValueError('proof report differs from receipt')
    result = copy.deepcopy(original)
    result['power']['switching_reconstruction'] = verified
    result['power']['artifact_sha256'] = dict(artifacts)
    result['revalidation'] = {'version': VERSION, 'policy': POLICY,
        'source_measurement': str(source.resolve()), 'source_sha256': receipt['measurement_sha256'],
        'receipt': str(receipt_path.resolve()), 'receipt_sha256': file_digest(receipt_path)[0],
        'source_artifact_sha256': original['power']['artifact_sha256'],
        'implementation_sha256': receipt['implementation_sha256'],
        'windows_implementation_sha256': receipt['windows_implementation_sha256'],
        'native_setup': native_setup(power), 'native_power_unchanged': True}
    return result


def inventory(out, reference_root):
    root = Path.cwd()
    archive = catalog.design(root, 'ibex', 'power')
    archive_hash = file_digest(archive)[0]
    ref_plan = read(reference_root / 'plan.json')
    refs = {}
    for case in ref_plan['cases']:
        path = reference_root / ('retry-' + case['id']) / 'measurement.json'
        complete = read(path.parent / 'complete.json')
        checked(path, complete['measurement_sha256'])
        record = read(path)
        if record['activity'] != case or record['plan_sha256'] != ref_plan['sha256']:
            raise ValueError('repaired reference selection differs')
        if not record['activity']['activity_solved']:
            raise ValueError('reference is not activity-qualified')
        compare_measurements(record, record)
        refs[case['target']] = {'path': str(path.resolve()), 'sha256': file_digest(path)[0]}
    if len(refs) != 8:
        raise ValueError('eight repaired references required')
    cases, seen, buckets = [], set(), []
    with gzip.open(archive, 'rt') as stream:
        for line in stream:
            bucket = json.loads(line)
            if bucket['bucket'] == 'references-ibex':
                continue
            if bucket['bucket'] not in ('baselines-ibex', 'flash-ibex', 'strong-ibex'):
                raise ValueError('unknown authoritative candidate bucket')
            buckets.append({k: bucket[k] for k in ('bucket', 'plan_sha256', 'plan_path', 'plan_file_sha256')})
            for row in bucket['records']:
                case = row['case']
                if case['target'].endswith('flat_control'):
                    continue
                if case.get('role') == 'power_reference' or row['status'] != 'measured':
                    raise ValueError('missing or invalid candidate')
                raw = row['raw_measurement'].encode()
                expected = row['receipt']['measurement_sha256']
                if digest(raw) != expected:
                    raise ValueError('archive measurement hash mismatch')
                record = json.loads(raw)
                if (record['activity'] != case or record['case_id'] != case['id']
                        or record['plan_sha256'] != bucket['plan_sha256']):
                    raise ValueError('archived selection mismatch')
                path = root / row['source']
                checked(path, expected)
                if read(path.parent.parent / 'complete.json') != row['receipt']:
                    raise ValueError('authoritative completion changed')
                if read(path.parent.parent.parent / 'collection.json')['plan_sha256'] != bucket['plan_sha256']:
                    raise ValueError('collection plan changed')
                identity = (case['policy'], case['target'], case['seed'])
                if identity in seen or case['domain'] != 'ibex-temporal':
                    raise ValueError('duplicate or non-Ibex candidate')
                seen.add(identity)
                reference = read(refs[case['target']]['path'])
                if native_setup(record['power']) != native_setup(reference['power']):
                    raise ValueError('candidate/repaired-reference timing or model differs')
                compare_measurements(record, reference)  # Validate native shape/task before replay.
                strict = reconstruction(record['power']['full']['leaf_switching_sum_w'],
                                        record['power']['weighted_leaf_switching_w'])['pass']
                if strict != record['power']['switching_additivity_pass']:
                    raise ValueError('native additivity flag differs from totals')
                cases.append({'case_id': case['id'], 'method': case['policy'], 'target': case['target'],
                              'seed': case['seed'], 'source': str(path.resolve()), 'source_sha256': expected,
                              'strict_pass': strict, 'reference': refs[case['target']]})
    if len(cases) != 400 or Counter(c['method'] for c in cases) != Counter({a: 80 for a in ARMS}):
        raise ValueError('authoritative nonflat inventory is not 400 / 80 per method')
    out.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), Path(__file__).with_name('reconstruction_audit.py'),
               Path(__file__).with_name('windows.py'),
               Path(__file__).parents[2] / 'reporting/power_reference.py']
    hashes = {}
    for source in sources:
        saved = out / ('source-' + source.name)
        saved.write_bytes(source.read_bytes())
        hashes[str(source.resolve())] = file_digest(saved)[0]
    data = {'version': VERSION, 'archive': str(archive), 'archive_sha256': archive_hash,
            'selection': 'Authoritative frozen archive, all five methods, all eight nonflat tasks, ten seeds each.',
            'plan_provenance': 'Original plan paths no longer present; archived cases, plan identities, collection identities and completion hashes verified.',
            'buckets': buckets, 'references': refs, 'cases': cases, 'implementation_sha256': hashes,
            'strict_pass_count': sum(c['strict_pass'] for c in cases),
            'audit_required_count': sum(not c['strict_pass'] for c in cases)}
    write(out / 'inventory.json', data)
    return data


def cleanup_waveform(audit, source, batch):
    """Delete only this batch's disposable restored VCD, retaining verified zstd."""
    temporary = audit / 'power_gls.vcd'
    if not temporary.exists():
        return
    if (temporary.is_symlink() or not temporary.resolve().is_relative_to(batch.resolve())
            or temporary.resolve() == source.resolve()):
        raise ValueError('unsafe temporary waveform cleanup')
    receipt_path = source.with_suffix('.vcd.retention.json')
    receipt = read(receipt_path)
    packed = source.with_suffix('.vcd.zst')
    if receipt['encoding'] != 'zstd':
        raise ValueError('unsupported retained waveform')
    checked(packed, receipt['retained_sha256'])
    if file_digest(temporary) != (receipt['sha256'], receipt['bytes']):
        raise ValueError('temporary waveform does not match retained original')
    write(audit / 'cleanup.json', {'temporary': str(temporary), 'retained': str(packed),
                                  'retention_receipt': str(receipt_path), 'sha256': receipt['sha256'],
                                  'recoverable': True, 'bytes': receipt['bytes']})
    temporary.unlink()


def process_case(case, batch):
    destination = batch / 'cases' / case['case_id']
    destination.mkdir(parents=True, exist_ok=True)
    status = destination / 'status.json'
    try:
        source = Path(case['source'])
        checked(source, case['source_sha256'])
        checked(case['reference']['path'], case['reference']['sha256'])
        original, reference = read(source), read(case['reference']['path'])
        if native_setup(original['power']) != native_setup(reference['power']):
            raise ValueError('cross-setup candidate/reference')
        complete = destination / 'complete.json'
        if complete.exists():
            checkpoint = read(complete)
            checked(destination / 'measurement.json', checkpoint['measurement_sha256'])
            revised = read(destination / 'measurement.json')
            compare_measurements(revised, reference)
        else:
            write(status, {'state': 'running', 'case_id': case['case_id'], 'source': str(source)})
            if case['strict_pass']:
                # Byte-for-byte preservation, including its legacy policy metadata.
                (destination / 'measurement.json').write_bytes(source.read_bytes())
                revised = original
            else:
                audit = destination / 'audit'
                audit_archived(source, audit, workers=3, resume=True, timeout_s=1200)
                receipt_path = audit / 'receipt.json'
                receipt = read(receipt_path)
                revised = revised_measurement(original, receipt, receipt_path)
                compare_measurements(revised, reference)
                write(destination / 'measurement.json', revised)
            compare_measurements(revised, reference)
            checked(source, case['source_sha256'])
            write(complete, {'measurement_sha256': file_digest(destination / 'measurement.json')[0],
                             'source_sha256': case['source_sha256'], 'version': VERSION,
                             'reference_sha256': case['reference']['sha256']})
        if not case['strict_pass']:
            cleanup_waveform(destination / 'audit', source.parent / 'gls/power_gls.vcd', batch)
        result = {'state': 'strict_preserved' if case['strict_pass'] else 'slew_verified',
                  'case_id': case['case_id'], 'method': case['method'], 'target': case['target'],
                  'measurement': str((destination / 'measurement.json').resolve()),
                  'measurement_sha256': file_digest(destination / 'measurement.json')[0],
                  'source': str(source), 'source_sha256': case['source_sha256']}
    except Exception as error:
        result = {'state': 'failed', 'case_id': case['case_id'], 'method': case['method'],
                  'target': case['target'], 'error': repr(error), 'source': case['source']}
    write(status, result)
    print(json.dumps(result), flush=True)
    return result


def run_batch(out, workers=8):
    data = read(out / 'inventory.json')
    for source, expected in data['implementation_sha256'].items():
        checked(source, expected)
    checked(data['archive'], data['archive_sha256'])
    results = {}
    lock = (out / 'runner.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def progress(active=()):
        counts = Counter(r['state'] for r in results.values())
        write(out / 'progress.json', {'version': VERSION, 'updated_unix_s': time.time(),
              'total': len(data['cases']), 'completed': len(results), 'counts': dict(counts),
              'running': list(active), 'pending': len(data['cases'])-len(results)-len(active),
              'case_workers': workers, 'sta_workers_per_case': 3})
        write(out / 'index.json', {'version': VERSION, 'records': list(results.values()),
                                 'inventory_sha256': file_digest(out / 'inventory.json')[0]})

    # Preserve strict passes first so consumers immediately have their unchanged records.
    for case in data['cases']:
        if case['strict_pass']:
            results[case['case_id']] = process_case(case, out)
    pending = iter(c for c in data['cases'] if not c['strict_pass'])
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,
            mp_context=multiprocessing.get_context('spawn')) as pool:
        active = {}
        def submit():
            case = next(pending, None)
            if case:
                active[pool.submit(process_case, case, out)] = case['case_id']
        for _ in range(workers):
            submit()
        progress(active.values())
        while active:
            done, _ = concurrent.futures.wait(active, timeout=15,
                                             return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                case_id = active.pop(future)
                try:
                    results[case_id] = future.result()
                except Exception as error:
                    results[case_id] = {'case_id': case_id, 'state': 'failed', 'error': repr(error)}
                submit()
            progress(active.values())
    progress()
    write(out / 'summary.json', {'version': VERSION, 'total': len(results),
          'counts': dict(Counter(r['state'] for r in results.values())),
          'all_passed': all(r['state'] != 'failed' for r in results.values()),
          'index_sha256': file_digest(out / 'index.json')[0]})
    lock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('inventory', 'run'))
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--references', type=Path,
                        default=Path('out/reference-repair-v1/power-preparation-v2/ibex'))
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    if args.action == 'inventory':
        data = inventory(args.out.resolve(), args.references.resolve())
        print(json.dumps({k: data[k] for k in ('strict_pass_count', 'audit_required_count')}))
    else:
        if not 1 <= args.workers <= 8:
            raise ValueError('one to eight bounded case workers required')
        run_batch(args.out.resolve(), args.workers)


if __name__ == '__main__':
    main()
