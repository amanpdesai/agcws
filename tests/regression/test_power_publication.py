"""Publication retains failures and compares identical measured subsets."""

import copy
import gzip
import importlib.util
import json
from pathlib import Path

import pytest

SPEC=importlib.util.spec_from_file_location('power_publication','paper/scripts/extract_power.py')
power=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(power)


def test_compact_measurement_hash_and_selection():
    bucket=json.loads(gzip.decompress(Path('results/aes/power/measurements.jsonl.gz').read_bytes()).splitlines()[0])
    row=bucket['records'][0]
    record=power.unpack_record(row)
    assert record['case_id']==row['case']['id']
    changed=copy.deepcopy(row)
    changed['raw_measurement']+=' '
    with pytest.raises(ValueError,match='hash mismatch'):
        power.unpack_record(changed)
    changed=copy.deepcopy(row)
    changed['case']['seed']=-1
    with pytest.raises(ValueError,match='selection mismatch'):
        power.unpack_record(changed)


def test_no_failures_silently_filled_and_matched_redmule():
    summary=json.loads(Path('results/summaries/power.json').read_text())
    coverage=[c for d in summary['designs'].values() for c in d['coverage'].values()]
    assert sum(c['planned'] for c in coverage)==2295
    assert sum(c['measured'] for c in coverage)==2295
    assert sum(c['failed'] for c in coverage)==0
    assert sum(c.get('recovered', 0) for c in coverage)==22
    red=summary['designs']['redmule']
    for arm,pair in red['matched_strong'].items():
        assert pair['strong']['n']==pair['comparator']['n']
        assert pair['strong']['n']==red['nonflat_by_arm'][arm]['n']
    assert red['matched_strong']['phase-ga']['strong']['n']==80
    assert len(red['recovered_failures']) == 22
    assert not red['failures']
    assert red['qualified_reference_by_arm']['strong-medium-64k']['n']==80


def test_repaired_references_and_ibex_validation():
    summary=json.loads(Path('results/summaries/power.json').read_text())
    assert summary['power_revision']=='power-revision-v2'
    references=[r for d in summary['designs'].values() for t,r in d['references'].items()
                if not t.endswith('flat_control')]
    assert len(references)==40 and all(r['reference_activity_solved'] for r in references)
    ibex=summary['designs']['ibex']['reconstruction_counts']
    assert ibex['nonflat_candidates_strict']==193
    assert ibex['nonflat_candidates_slew_verified']==207
    assert ibex['nonflat_references_slew_verified']==8
    sensitivity=summary['excluding_ibex']
    assert sensitivity['matched_pairs']==320
    assert sensitivity['lower_strong_mean_on_each_remaining_design']
    assert sum(d['nonflat_by_arm']['strong-medium-64k']['better_than_constant']
               for d in summary['designs'].values())==399
    red=summary['designs']['redmule']['exclusions_by_arm']
    assert [red[a]['total'] for a in power.ARMS]==[0,0,0,0,0]
    assert [red[a]['nonflat'] for a in power.ARMS]==[0,0,0,0,0]
    recovered=summary['designs']['redmule']['recovered_failures']
    assert [sum(r['case']['policy']==a for r in recovered) for a in power.ARMS]==[0,4,12,6,0]


def test_constant_reference_diagnostic_is_undefined_not_zero():
    row=dict(nrmse=.1,max_bin_error=.1,best_constant_nrmse=0.,
             error_over_constant_floor=None,reference_activity_solved=False)
    assert power.describe([row])['mean_error_over_constant_floor'] is None
    assert power.describe([])=={'n':0}


def test_revision_hashes_and_paths_are_checked(tmp_path, monkeypatch):
    monkeypatch.setattr(power, 'ROOT', tmp_path)
    path = tmp_path / 'measurement.json'
    path.write_text('{}')
    entry = dict(path='measurement.json', sha256=power.digest(path.read_bytes()))
    assert power.checked_json(entry, {}) == {}
    path.write_text('{"changed":true}')
    with pytest.raises(ValueError, match='hash mismatch'):
        power.checked_json(entry, {})
    with pytest.raises(ValueError, match='unsafe catalog path'):
        power.checked_json(dict(path='../measurement.json', sha256=entry['sha256']), {})


def test_candidate_revision_cannot_change_search_or_native_power(tmp_path, monkeypatch):
    bucket = json.loads(gzip.decompress(Path('results/aes/power/measurements.jsonl.gz').read_bytes()).splitlines()[0])
    row = bucket['records'][0]
    original = power.unpack_record(row)
    original['_archive_sha256'] = row['receipt']['measurement_sha256']
    monkeypatch.setattr(power, 'ROOT', tmp_path)
    path = tmp_path / 'measurement.json'
    for field in ('activity', 'gate_dynamic_power_w'):
        changed = copy.deepcopy(original)
        changed.pop('_archive_sha256')
        changed[field] = {} if field == 'activity' else [0]*8
        path.write_text(json.dumps(changed))
        entry = dict(path=path.name, sha256=power.digest(path.read_bytes()),
                     original_sha256=original['_archive_sha256'])
        with pytest.raises(ValueError, match='changes frozen'):
            power.revised_candidate(original, entry, {})
    changed = copy.deepcopy(original)
    changed['power']['clock_period_s'] *= 2
    path.write_text(json.dumps(changed))
    entry['sha256'] = power.digest(path.read_bytes())
    with pytest.raises(ValueError, match='changes native power'):
        power.revised_candidate(original, entry, {})


def test_excluding_ibex_sensitivity_uses_matched_weights():
    def result(n, a, b):
        return {'matched_strong': {arm: {'strong': {'n': n, 'mean_nrmse': a},
            'comparator': {'n': n, 'mean_nrmse': b}} for arm in power.ARMS[:3]}}
    rows = {'aes': result(80, .01, .1), 'redmule': result(76, .03, .2),
            'ibex': result(80, 100, 0)}
    got = power.sensitivity(rows)
    assert got['matched_pairs'] == 156
    assert got['lower_strong_mean_on_each_remaining_design']
    assert got['mean_strong_nrmse'] == pytest.approx((80*.01+76*.03)/156)
