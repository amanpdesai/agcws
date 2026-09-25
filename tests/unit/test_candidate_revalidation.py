import copy
import json

import pytest

from agcws.evaluation.power import candidate_revalidation as batch
from agcws.evaluation.power.candidate_overlay import verify_revision


def test_completed_case_resume_never_replays_sta(tmp_path, monkeypatch):
    original = sample()
    source = tmp_path / 'source.json'
    source.write_text(json.dumps(original))
    checksum = batch.file_digest(source)[0]
    case = {'case_id': 'case', 'source': str(source), 'source_sha256': checksum,
            'reference': {'path': str(source), 'sha256': checksum},
            'strict_pass': False, 'method': 'test', 'target': 'step'}
    destination = tmp_path / 'batch/cases/case'
    destination.mkdir(parents=True)
    (destination / 'measurement.json').write_bytes(source.read_bytes())
    batch.write(destination / 'complete.json', {'measurement_sha256': checksum})
    calls = []
    monkeypatch.setattr(batch, 'compare_measurements', lambda *args: calls.append('validate'))
    monkeypatch.setattr(batch, 'cleanup_waveform', lambda *args: calls.append('cleanup'))
    def forbidden(*args, **kwargs):
        pytest.fail('completed checkpoint must not replay STA')
    monkeypatch.setattr(batch, 'audit_archived', forbidden)
    result = batch.process_case(case, tmp_path / 'batch')
    assert result['state'] == 'slew_verified'
    assert calls == ['validate', 'cleanup']


def test_overlay_pending_and_failed_are_not_all_passed(tmp_path, monkeypatch):
    from agcws.evaluation.power import candidate_overlay as overlay
    monkeypatch.chdir(tmp_path)
    work = tmp_path / 'batch'
    work.mkdir()
    archive = tmp_path / 'archive.gz'
    archive.write_bytes(b'archive')
    inventory = {'archive': str(archive), 'archive_sha256': batch.file_digest(archive)[0],
                 'implementation_sha256': {}, 'references': {}, 'buckets': {},
                 'audit_required_count': 1, 'strict_pass_count': 193,
                 'cases': [{'case_id': 'case', 'strict_pass': False}]}
    batch.write(work / 'inventory.json', inventory)
    destination = tmp_path / 'results/ibex/power/test-audit'
    index = overlay.publish(work, destination)
    assert not index['complete'] and not index['all_passed']
    provenance = 'results/ibex/power/test-audit/provenance.json'
    assert index['inputs'][provenance] == batch.file_digest(tmp_path / provenance)[0]
    (work / 'cases/case').mkdir(parents=True)
    batch.write(work / 'cases/case/status.json', {'state': 'failed', 'error': 'unexplained'})
    index = overlay.publish(work, destination)
    assert index['complete'] and not index['all_passed']
    assert 'case' in index['failed'] and not index['entries']


def sample():
    return {'case_id': 'case', 'activity': {'target': 'step', 'domain': 'ibex-temporal'},
            'gate_dynamic_power_w': [1.]*8,
            'power': {'inputs': {'a/mapped.v': 'net', 'a/cells.lib': 'lib', 'a/sta': 'tool'},
                      'scope': 'dut', 'clock_period_s': 1e-8, 'tool_version': 'pinned',
                      'full': {'leaf_switching_sum_w': 1.},
                      'windows': [{'leaf_switching_sum_w': .9}]*8,
                      'grid': {'durations_s': [1e-6]*8}, 'weighted_leaf_switching_w': .9,
                      'switching_reconstruction': {'policy': 'ibex-10ns-estimate-v1'},
                      'artifact_sha256': {'full.rpt': 'old'}}}


def setup_receipt(tmp_path):
    original = sample()
    source = tmp_path / 'original.json'
    source.write_text(json.dumps(original))
    report = tmp_path / 'full.rpt'
    report.write_text('diagnostic report')
    checksum = batch.file_digest(report)[0]
    receipt = {'native_power': copy.deepcopy(original['power']),
               'source_inputs': copy.deepcopy(original['power']['inputs']), 'target': 'step',
               'measurement': str(source), 'measurement_sha256': batch.file_digest(source)[0],
               'switching_reconstruction': {'proof': {'report_sha256': {str(report): checksum}}},
               'artifact_sha256': {'full.rpt': checksum},
               'implementation_sha256': 'impl', 'windows_implementation_sha256': 'windows'}
    path = tmp_path / 'receipt.json'
    path.write_text(json.dumps(receipt))
    return original, receipt, path


def test_revision_preserves_case_and_all_native_data(tmp_path, monkeypatch):
    original, receipt, path = setup_receipt(tmp_path)
    monkeypatch.setattr(batch, 'reconstruction', lambda *args, **kwargs: {
        'policy': 'slew-verified-v1', 'accepted_estimate': True, 'proof': kwargs['proof']})
    revised = batch.revised_measurement(original, receipt, path)
    verify_revision(original, revised)
    assert revised['activity'] == original['activity']
    assert 'reconstruction_policy' not in revised['activity']
    assert revised['power']['inputs'] == original['power']['inputs']
    assert revised['revalidation']['source_sha256'] == receipt['measurement_sha256']
    assert original['power']['artifact_sha256'] == {'full.rpt': 'old'}


@pytest.mark.parametrize('change', ['clock', 'netlist', 'library', 'tool', 'vector', 'activity'])
def test_cross_setup_or_native_changes_cannot_publish(change):
    original = sample()
    revised = copy.deepcopy(original)
    revised['power']['switching_reconstruction']['policy'] = 'slew-verified-v1'
    if change == 'clock':
        revised['power']['clock_period_s'] = 1e-7
    elif change in ('netlist', 'library', 'tool'):
        name = {'netlist': 'a/mapped.v', 'library': 'a/cells.lib', 'tool': 'a/sta'}[change]
        revised['power']['inputs'][name] = 'other'
    elif change == 'vector':
        revised['gate_dynamic_power_w'][0] = 2.
    else:
        revised['activity']['reconstruction_policy'] = 'slew-verified-v1'
    with pytest.raises(ValueError):
        verify_revision(original, revised)


def test_receipt_from_another_setup_rejected(tmp_path):
    original, receipt, path = setup_receipt(tmp_path)
    receipt['native_power']['inputs']['a/mapped.v'] = 'other'
    with pytest.raises(ValueError, match='different measurement/setup'):
        batch.revised_measurement(original, receipt, path)


def test_failed_proof_does_not_generate_revision(tmp_path, monkeypatch):
    original, receipt, path = setup_receipt(tmp_path)
    monkeypatch.setattr(batch, 'reconstruction', lambda *args, **kwargs: {'accepted_estimate': False})
    with pytest.raises(ValueError, match='failed or incomplete'):
        batch.revised_measurement(original, receipt, path)


def test_changed_diagnostic_report_rejected(tmp_path, monkeypatch):
    original, receipt, path = setup_receipt(tmp_path)
    monkeypatch.setattr(batch, 'reconstruction', lambda *args, **kwargs: {
        'policy': 'slew-verified-v1', 'accepted_estimate': True, 'proof': kwargs['proof']})
    (tmp_path / 'full.rpt').write_text('tampered')
    with pytest.raises(ValueError, match='changed source'):
        batch.revised_measurement(original, receipt, path)


def test_cleanup_preserves_original_lossless_source(tmp_path):
    root = tmp_path / 'batch'
    audit = root / 'cases/case/audit'
    audit.mkdir(parents=True)
    archive = tmp_path / 'archive'
    archive.mkdir()
    source = archive / 'power_gls.vcd'
    packed = source.with_suffix('.vcd.zst')
    packed.write_bytes(b'lossless retained fixture')
    temporary = audit / 'power_gls.vcd'
    temporary.write_bytes(b'waveform fixture')
    checksum, size = batch.file_digest(temporary)
    source.with_suffix('.vcd.retention.json').write_text(json.dumps({
        'encoding': 'zstd', 'retained_sha256': batch.file_digest(packed)[0],
        'sha256': checksum, 'bytes': size}))
    batch.cleanup_waveform(audit, source, root)
    assert not temporary.exists()
    assert packed.read_bytes() == b'lossless retained fixture'
    assert batch.read(audit / 'cleanup.json')['recoverable']


def test_cleanup_refuses_source_or_outside_batch(tmp_path):
    audit = tmp_path / 'original'
    audit.mkdir()
    source = audit / 'power_gls.vcd'
    source.write_bytes(b'original')
    with pytest.raises(ValueError, match='unsafe'):
        batch.cleanup_waveform(audit, source, tmp_path / 'batch')
    assert source.read_bytes() == b'original'
