"""Final power records are complete, validated, and compared on matched runs."""

import copy
import gzip
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from agcws.evidence.power import checked_bytes
from agcws.evidence.power import load as load_power

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
    red=summary['designs']['redmule']
    for arm,pair in red['matched_strong'].items():
        assert pair['strong']['n']==pair['comparator']['n']
        assert pair['strong']['n']==red['nonflat_by_arm'][arm]['n']
    assert red['matched_strong']['phase-ga']['strong']['n']==80
    assert not red['failures']
    assert red['qualified_reference_by_arm']['strong-medium-64k']['n']==80


def test_qualified_references_and_ibex_validation():
    summary=json.loads(Path('results/summaries/power.json').read_text())
    assert summary['version']==3 and 'power_revision' not in summary
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
    buckets, _ = load_power(Path.cwd(), 'redmule')
    audited = [r for b in buckets for r in b['records'] if r.get('validation') == 'clipping']
    assert [sum(r['case']['policy']==a for r in audited) for a in power.ARMS]==[0,4,12,6,0]
    assert all(r['failures'] for r in audited)


def test_constant_reference_diagnostic_is_undefined_not_zero():
    row=dict(nrmse=.1,max_bin_error=.1,best_constant_nrmse=0.,
             error_over_constant_floor=None,reference_activity_solved=False)
    assert power.describe([row])['mean_error_over_constant_floor'] is None
    assert power.describe([])=={'n':0}


def test_evidence_hashes_and_paths_are_checked(tmp_path):
    path = tmp_path / 'measurement.json'
    path.write_text('{}')
    entry = dict(path='measurement.json', sha256=power.digest(path.read_bytes()))
    assert json.loads(checked_bytes(tmp_path, entry)) == {}
    path.write_text('{"changed":true}')
    with pytest.raises(ValueError, match='hash mismatch'):
        checked_bytes(tmp_path, entry)
    with pytest.raises(ValueError, match='unsafe catalog path'):
        checked_bytes(tmp_path, dict(path='../measurement.json', sha256=entry['sha256']))


def test_final_archive_needs_no_revision_overlay():
    for design in power.DESIGNS:
        buckets, records = load_power(Path.cwd(), design)
        assert len(records) == 459
        assert all(row['status'] == 'measured' for b in buckets for row in b['records'])
        refs = {m['activity']['target']:m for m in records.values()
                if m['activity'].get('role') == 'power_reference'}
        assert len(refs) == 9
        for record in records.values():
            power.compare_measurements(record, refs[record['activity']['target']])


def test_unpacked_plan_must_match_record():
    bucket=json.loads(gzip.decompress(Path('results/aes/power/measurements.jsonl.gz').read_bytes()).splitlines()[0])
    row=copy.deepcopy(bucket['records'][0])
    row['plan_sha256'] = 'wrong'
    with pytest.raises(ValueError, match='plan mismatch'):
        power.unpack_record(row)


@pytest.mark.parametrize('change', ['failed', 'duplicate', 'proof', 'source'])
def test_final_inventory_rejects_missing_or_mismatched_evidence(tmp_path, change):
    root = Path.cwd()
    shutil.copytree(root / 'results/aes/power', tmp_path / 'results/aes/power')
    shutil.copytree(root / 'results/aes/tasks/references', tmp_path / 'results/aes/tasks/references')
    shutil.copy2(root / 'results/index.json', tmp_path / 'results/index.json')
    catalog = json.loads((tmp_path / 'results/index.json').read_text())
    archive = tmp_path / 'results/aes/power/measurements.jsonl.gz'
    buckets = [json.loads(line) for line in gzip.decompress(archive.read_bytes()).splitlines()]
    if change == 'failed':
        buckets[0]['records'][0]['status'] = 'failed'
    elif change == 'duplicate':
        buckets[0]['records'].append(buckets[0]['records'][0])
    elif change == 'proof':
        proof = tmp_path / 'results/aes/power/validation/references.json.gz'
        proof.write_bytes(proof.read_bytes() + b' ')
    else:
        buckets[0]['records'][0]['plan_sha256'] = 'another-plan'
    raw = ''.join(json.dumps(b) + '\n' for b in buckets).encode()
    archive.write_bytes(gzip.compress(raw, mtime=0))
    catalog['designs']['aes']['power_sha256'] = power.digest(archive.read_bytes())
    (tmp_path / 'results/index.json').write_text(json.dumps(catalog))
    with pytest.raises(ValueError):
        load_power(tmp_path, 'aes')


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
