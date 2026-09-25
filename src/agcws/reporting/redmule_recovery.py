"""Publish verified RedMulE power measurements without altering native estimates."""

import argparse
import concurrent.futures
import copy
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

from agcws.evaluation.power.reconstruction_audit import LIBERTY_SHA256, instrument_tcl, slew_proof
from agcws.evaluation.power.windows import aligned_grids, reconstruction
from agcws.evidence.retention import file_digest
from agcws.reporting.power_reference import compare_measurements

VERSION = 'redmule-slew-recovery-v1'
DIRECTORY = Path('results/redmule/power/slew-recovery-v1')
ARCHIVE = Path('results/redmule/power/measurements.jsonl.gz')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def failed_records(root):
    with gzip.open(root / ARCHIVE, 'rt') as stream:
        return [(bucket['plan_sha256'], row)
                for bucket in map(json.loads, stream) for row in bucket['records']
                if row['status'] == 'failed']


def recover(plan_hash, row, evidence):
    """Reject mismatched execution, power, or proof before creating a measurement."""
    case = row['case']
    request, rtl, functional = (evidence[k] for k in ('request', 'rtl', 'functional'))
    power = copy.deepcopy(evidence['power'])
    if (case['domain'] != 'redmule-temporal-long' or request['case'] != case
            or request['plan_sha256'] != plan_hash):
        raise ValueError('recovery differs from frozen selection')
    if not rtl['valid'] or rtl['rates'] != case['rates']:
        raise ValueError('RTL replay differs from selected activity')
    jobs = sum(p['jobs'] for p in case['program']['phases'])
    completions = functional['job_completions']
    if (functional['valid'] is not True or functional['completed_jobs'] != jobs
            or functional['checked_outputs'] != jobs * case['program']['size']**2
            or functional['useful_work'] != rtl['profile']['useful_work']
            or len(completions) != jobs
            or any(j != i or not 0 <= cycle < 262144 or errors != 0
                   for i, (j, cycle, errors) in enumerate(completions))):
        raise ValueError('functional/work/deadline check failed')
    if power['clock_period_s'] != 1e-8 or not aligned_grids(power['rtl_grid'], power['grid']):
        raise ValueError('recovery window alignment differs')
    libs = [h for p, h in power['inputs'].items() if p.endswith('.lib')]
    if libs != [LIBERTY_SHA256]:
        raise ValueError('unsupported recovery library')
    diagnostic = reconstruction(power['full']['leaf_switching_sum_w'],
        power['weighted_leaf_switching_w'], policy='slew-verified-v1',
        top='agcws_redmule_4x4', period_s=power['clock_period_s'], proof=evidence['proof'],
        window_values=[w['leaf_switching_sum_w'] for w in power['windows']],
        durations_s=power['grid']['durations_s'])
    if not diagnostic['accepted_estimate'] or power['switching_additivity_pass']:
        raise ValueError('failed recovery proof or case did not require recovery')
    power['switching_reconstruction'] = diagnostic
    power['artifact_sha256'] = {
        Path(p).name: h for p, h in evidence['proof']['report_sha256'].items()}
    fractions = [r['annotated_pins'] / (r['annotated_pins'] + r['unannotated_pins'])
                 for r in [power['full'], *power['windows']]]
    if len(fractions) != 9 or min(fractions) < request['minimum_pin_annotation_fraction']:
        raise ValueError('insufficient annotation')
    result = dict(version='finalist-power-v1', case_id=case['id'], plan_sha256=plan_hash,
        activity=case, gate_dynamic_power_w=[w['dynamic_power_w'] for w in power['windows']],
        gate_dynamic_energy_j=[w['dynamic_power_w'] * d for w, d in
                              zip(power['windows'], power['grid']['durations_s'])],
        pin_annotation_fractions=fractions, power=power,
        recovery=dict(version=VERSION, original_failures=row['failures'],
                      native_power_unchanged=True),
        claim='Zero-delay mapped-gate dynamic power; not signoff or power-target attainment.')
    reference = copy.deepcopy(result)
    reference['activity'] = {**case, 'role': 'power_reference'}
    compare_measurements(result, reference)
    return result


def audit(root, diagnostics, workers=8):
    """Reproduce native reports with diagnostic queries, without modifying activity."""
    def one(item):
        _, row = item
        case_id = row['case']['id']
        source = (root / row['failures'][-1]['path']).parent / 'power'
        native = read(source / 'power.json')
        directory = diagnostics / case_id
        directory.mkdir(parents=True, exist_ok=False)
        old_lib = next(p for p in native['inputs'] if p.endswith('.lib'))
        library = root / 'benchmarks/support/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib'
        tool = next(p for p in native['inputs'] if p.endswith('/sta'))
        if file_digest(library)[0] != native['inputs'][old_lib] or file_digest(Path(tool))[0] != native['inputs'][tool]:
            raise ValueError('diagnostic tool or library changed')
        names = ['full', *[f'bin-{i}' for i in range(8)]]
        def window(name):
            script = instrument_tcl((source / f'{name}.tcl').read_text().replace(old_lib, str(library)))
            path = directory / f'{name}.tcl'
            path.write_text(script)
            with (directory / f'{name}.rpt').open('w') as log:
                subprocess.run([tool, '-no_init', '-exit', str(path)], stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=1200)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(window, names))
        proof = slew_proof([directory / f'{n}.rpt' for n in names],
                           native['grid']['durations_s'], [native['full'], *native['windows']])
        (directory / 'diagnostic.json').write_text(json.dumps(proof, indent=2)+'\n')
        if not proof['pass']:
            raise ValueError(f'clipping audit failed: {case_id}')
        print('Audited', case_id, flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, failed_records(root)))


def capture(root, diagnostics, workers=8):
    """Bind the completed signal-level audit to preserved execution evidence."""
    directory = root / DIRECTORY
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / 'index.json').exists():
        raise ValueError('published recovery already exists; verify instead')
    def one(item):
        plan_hash, row = item
        case_id = row['case']['id']
        failure = row['failures'][-1]
        source = root / failure['path']
        if file_digest(source)[0] != failure['sha256']:
            raise ValueError('archived failure changed')
        attempt = source.parent
        names = dict(request='request.json', rtl='rtl/replay-result.json',
                     functional='gls/functional.json', power='power/power.json')
        evidence = {key: read(attempt / name) for key, name in names.items()}
        native = evidence['power']
        # Verify original reports and the exact numerical/tool inputs still on disk.
        for name, sha in native['artifact_sha256'].items():
            if Path(name).name != name or file_digest(attempt / 'power' / name)[0] != sha:
                raise ValueError('native power report changed')
        for name, sha in native['inputs'].items():
            if not (name.endswith(('.vcd', '.lib', '/mapped.v', '/sta'))):
                continue
            path = root / 'benchmarks/support/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib' if name.endswith('.lib') else Path(name)
            if file_digest(path)[0] != sha:
                raise ValueError(f'power input changed: {name}')
        reports = [diagnostics / case_id / f'{name}.rpt'
                   for name in ['full', *[f'bin-{i}' for i in range(8)]]]
        evidence['proof'] = json.loads(json.dumps(slew_proof(
            reports, native['grid']['durations_s'], [native['full'], *native['windows']])))
        if evidence['proof'] != read(diagnostics / case_id / 'diagnostic.json'):
            raise ValueError('saved audit does not reproduce')
        evidence['source_hashes'] = {str(attempt / name): file_digest(attempt / name)[0]
                                     for name in names.values()}
        evidence['source_hashes'].update(native['inputs'])
        measurement = recover(plan_hash, row, evidence)
        raw = (json.dumps(measurement, indent=2)+'\n').encode()
        destination = directory / f'{case_id}.json'
        if destination.exists() and destination.read_bytes() != raw:
            raise ValueError('partial recovery differs; use a new version')
        destination.write_bytes(raw)
        print('Recovered', case_id, flush=True)
        return case_id, evidence
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        cases = dict(pool.map(one, failed_records(root)))
    if len(cases) != 22:
        raise ValueError('expected the 22 archived RedMulE failures')
    bundle = directory / 'evidence.json.gz'
    bundle.write_bytes(gzip.compress(json.dumps(cases, sort_keys=True).encode(), mtime=0))
    entries = {case_id: {'path': str(DIRECTORY / f'{case_id}.json'),
                         'sha256': file_digest(directory / f'{case_id}.json')[0]}
               for case_id in cases}
    index = dict(version=VERSION, complete=True, entries=entries,
        inputs={str(ARCHIVE): file_digest(root / ARCHIVE)[0],
                str(DIRECTORY / 'evidence.json.gz'): file_digest(bundle)[0]},
        implementation_sha256={str(Path(__file__).relative_to(root)): file_digest(Path(__file__))[0]})
    (directory / 'index.json').write_text(json.dumps(index, indent=2)+'\n')
    return verify(root)


def verify(root):
    """Portable validation of execution, native numbers, and hash-bound proof receipts."""
    directory = root / DIRECTORY
    index = read(directory / 'index.json')
    if index['version'] != VERSION or index.get('complete') is not True:
        raise ValueError('incomplete recovery index')
    for name, sha in index['inputs'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or file_digest(root / name)[0] != sha:
            raise ValueError('recovery evidence checksum/path differs')
    with gzip.open(directory / 'evidence.json.gz', 'rt') as stream:
        cases = json.load(stream)
    rows = failed_records(root)
    expected = {row['case']['id'] for _, row in rows}
    if set(cases) != expected or set(index['entries']) != expected or len(expected) != 22:
        raise ValueError('recovery does not cover the archived failures exactly')
    measurements = {}
    for plan_hash, row in rows:
        case_id = row['case']['id']
        entry = index['entries'][case_id]
        if entry['path'] != str(DIRECTORY / f'{case_id}.json'):
            raise ValueError('unsafe recovery measurement path')
        path = root / entry['path']
        if file_digest(path)[0] != entry['sha256']:
            raise ValueError('recovery measurement checksum differs')
        record = recover(plan_hash, row, cases[case_id])
        if read(path) != record:
            raise ValueError('published recovery differs from native evidence')
        measurements[case_id] = record
    return measurements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, help='Completed per-case diagnostic directory')
    parser.add_argument('--audit', type=Path, help='Run signal-level checks into a new directory')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    root = Path.cwd()
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be between 1 and 16')
    if args.audit:
        audit(root, args.audit.resolve(), args.workers)
    result = capture(root, args.capture.resolve(), args.workers) if args.capture else (
        {} if args.audit else verify(root))
    print(json.dumps({'verified_recoveries': len(result)}))


if __name__ == '__main__':
    main()
