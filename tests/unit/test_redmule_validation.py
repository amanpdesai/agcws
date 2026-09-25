"""Recovered estimates must retain the original workload, execution, and power."""

import copy
import gzip
import json
from pathlib import Path

import pytest

from agcws.reporting.redmule_validation import (
    DIRECTORY,
    audited_records,
    measurement_from_evidence,
    verify,
)


@pytest.fixture
def saved_case():
    plan, row = audited_records(Path.cwd())[0]
    with gzip.open(DIRECTORY / 'clipping.json.gz', 'rt') as stream:
        evidence = json.load(stream)[row['case']['id']]
    return plan, row, evidence


def test_complete_portable_recovery():
    measurements = verify(Path.cwd())
    assert len(measurements) == 22
    assert all(m['recovery']['native_power_unchanged'] for m in measurements.values())
    assert all(not m['power']['switching_additivity_pass'] for m in measurements.values())
    assert all(m['power']['switching_reconstruction']['validation_pass'] for m in measurements.values())


@pytest.mark.parametrize('change', ['case', 'rtl', 'functional', 'deadline', 'annotation',
                                  'library', 'clock', 'power', 'missing_proof', 'unexplained'])
def test_recovery_rejects_invalid_or_stale_evidence(saved_case, change):
    plan, row, original = saved_case
    evidence = copy.deepcopy(original)
    if change == 'case':
        evidence['request']['case']['seed'] = -1
    elif change == 'rtl':
        evidence['rtl']['rates'][0] += 1
    elif change == 'functional':
        evidence['functional']['valid'] = False
    elif change == 'deadline':
        evidence['functional']['job_completions'][-1][1] = 262144
    elif change == 'annotation':
        evidence['power']['windows'][0]['unannotated_pins'] = 1000000
    elif change == 'library':
        name = next(p for p in evidence['power']['inputs'] if p.endswith('.lib'))
        evidence['power']['inputs'][name] = '0' * 64
    elif change == 'clock':
        evidence['power']['clock_period_s'] = 1e-7
    elif change == 'power':
        evidence['power']['windows'][0]['leaf_switching_sum_w'] += 1
    elif change == 'missing_proof':
        evidence['proof'] = {'pass': True}
    else:
        evidence['proof']['unexplained_difference_w'] = 1
    with pytest.raises(ValueError):
        measurement_from_evidence(plan, row, evidence)


def test_recovery_never_changes_native_values(saved_case):
    plan, row, evidence = saved_case
    result = measurement_from_evidence(plan, row, evidence)
    for field in ('full', 'windows', 'inputs', 'grid', 'rtl_grid', 'clock_period_s',
                  'weighted_means', 'weighted_leaf_switching_w'):
        assert result['power'][field] == evidence['power'][field]
    assert result['activity'] == row['case']
