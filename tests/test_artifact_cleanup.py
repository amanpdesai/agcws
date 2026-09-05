import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    'artifact_cleanup', Path(__file__).parents[1] / 'maintenance/clean_artifacts.py')
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


@pytest.mark.parametrize('name', ['..', '.', '../other', '/tmp', '.cache',
                                'aes-semantic-heldout-cpu', 'aes-core-synthesis'])
def test_cleanup_rejects_broad_or_protected_targets(tmp_path, name):
    with pytest.raises(ValueError):
        cleanup.target_path(tmp_path, name)


def test_cleanup_selects_only_waveforms_and_skips_symlinks(tmp_path):
    (tmp_path / 'activity.vcd').write_text('waveform')
    (tmp_path / 'activity.json').write_text('{}')
    (tmp_path / 'trials.jsonl').write_text('{}')
    (tmp_path / 'linked.fst').symlink_to(tmp_path / 'activity.vcd')
    assert list(cleanup.waveform_files(tmp_path)) == [tmp_path / 'activity.vcd']


def test_cleanup_rejects_modified_plan_entry(tmp_path):
    run = tmp_path / 'old-run'
    run.mkdir()
    trace = run / 'activity.vcd'
    trace.write_text('old')
    entry = {'path': 'old-run/activity.vcd', 'fingerprint': cleanup.fingerprint(trace)}
    assert cleanup.checked_file(tmp_path, entry, ['old-run']) == trace
    trace.write_text('changed')
    with pytest.raises(ValueError, match='changed'):
        cleanup.checked_file(tmp_path, entry, ['old-run'])


@pytest.mark.parametrize('path', ['../outside.vcd', '/tmp/outside.vcd', 'other/run.vcd'])
def test_cleanup_rejects_plan_escape(tmp_path, path):
    with pytest.raises(ValueError):
        cleanup.checked_file(tmp_path, {'path': path}, ['old-run'])


def test_cleanup_rejects_symlinked_target(tmp_path):
    (tmp_path / 'real').mkdir()
    (tmp_path / 'old-run').symlink_to(tmp_path / 'real', target_is_directory=True)
    with pytest.raises(ValueError):
        cleanup.target_path(tmp_path, 'old-run')


def test_plan_then_apply_retires_only_selected_waveforms(tmp_path, monkeypatch):
    root = tmp_path / 'out'
    run = root / 'old-run'
    run.mkdir(parents=True)
    (run / 'activity.vcd').write_text('regenerable trace')
    (run / 'trials.jsonl').write_text('research evidence')
    plan = root / 'cleanup.json'
    monkeypatch.setattr(cleanup, 'REPO', tmp_path)
    monkeypatch.setattr(cleanup, 'active_references', lambda *args: [])
    monkeypatch.setattr(cleanup.subprocess, 'check_output', lambda *args, **kwargs: b'')
    monkeypatch.setattr(sys, 'argv', ['clean', '--plan', str(plan), '--targets', 'old-run'])
    cleanup.main()
    assert (run / 'activity.vcd').exists()
    monkeypatch.setattr(sys, 'argv', ['clean', '--plan', str(plan), '--apply', '--retire'])
    cleanup.main()
    retired = root / 'retired/old-run'
    assert not (retired / 'activity.vcd').exists()
    assert (retired / 'trials.jsonl').read_text() == 'research evidence'
    assert plan.with_suffix('.deleted.jsonl').exists()
