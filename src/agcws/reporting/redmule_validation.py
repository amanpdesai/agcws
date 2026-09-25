"""Verify RedMulE clipping evidence against the final power inventory."""

import copy
import gzip
import json
from pathlib import Path

from agcws.evaluation.power.reconstruction_audit import LIBERTY_SHA256
from agcws.evaluation.power.windows import aligned_grids, reconstruction
from agcws.evidence.power import load as load_power
from agcws.evidence.power import unpack_record
from agcws.reporting.power_reference import compare_measurements

# Preserve the schema identity of the native validation receipt.
VERSION = 'redmule-slew-recovery-v1'
DIRECTORY = Path('results/redmule/power/validation')


def read(path):
    return json.loads(path.read_text())


def measurement_from_evidence(plan_hash, row, evidence):
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


def audited_records(root):
    buckets, _ = load_power(root, 'redmule')
    return [(row['plan_sha256'], row) for bucket in buckets for row in bucket['records']
            if row.get('validation') == 'clipping']


def verify(root):
    directory = root / DIRECTORY
    index = read(directory / 'index.json')
    with gzip.open(directory / 'clipping.json.gz', 'rt') as stream:
        cases = json.load(stream)
    rows = audited_records(root)
    expected = {row['case']['id'] for _, row in rows}
    if set(cases) != expected or set(index['entries']) != expected or len(expected) != 22:
        raise ValueError('clipping evidence does not cover the audited cases exactly')
    measurements = {}
    for plan_hash, row in rows:
        record = measurement_from_evidence(plan_hash, row, cases[row['case']['id']])
        if unpack_record(row) != record:
            raise ValueError('published measurement differs from native evidence')
        measurements[record['case_id']] = record
    return measurements


if __name__ == '__main__':
    print(json.dumps({'verified_measurements': len(verify(Path.cwd()))}))
