import copy
import json
import subprocess
import sys

import pytest

from agcws.analysis.ledger_audit import audit_scalar_cell


def cell():
    summary = {'budget': 2, 'policy': 'random', 'seed': 1, 'target': 0.5, 'epsilon': 0.02,
               'auc_best_so_far': 0.05, 'solved': True, 'right_censored': False,
               'evaluations_to_target': 2, 'valid_trials': 2, 'tokens_in': 0,
               'tokens_out': 0, 'est_cost_usd': 0.0}
    trials = [{'trial_id': str(i), 'policy': 'random', 'seed': 1,
               'goal': {'q': 0.5, 'tolerance': 0.02}, 'validity': {'valid': True},
               'profile': {'mean_power': power, 'useful_work': 38, 'valid': True},
               'loss': error, 'tokens_in': 0, 'tokens_out': 0, 'est_cost_usd': 0.0}
              for i, power, error in [(0, 6, 0.1), (1, 5, 0.0)]]
    return summary, trials, {'p_min': 0, 'p_max': 10, 'useful_work_floor': 38}


def test_audit_reconstructs_auc_and_censoring():
    assert audit_scalar_cell(*cell())['solved']


@pytest.mark.parametrize('field,value', [('auc_best_so_far', 0), ('tokens_in', 2),
                                        ('evaluations_to_target', 1), ('valid_trials', 1)])
def test_audit_rejects_corrupted_summary(field, value):
    summary, trials, calibration = cell()
    summary[field] = value
    with pytest.raises(ValueError):
        audit_scalar_cell(summary, trials, calibration)


def test_audit_rejects_stale_envelope():
    summary, trials, calibration = cell()
    calibration['p_max'] = 20
    with pytest.raises(ValueError, match='calibration'):
        audit_scalar_cell(summary, trials, calibration)


def test_audit_rejects_duplicate_proposals_ids():
    summary, trials, calibration = cell()
    trials[1] = copy.deepcopy(trials[0])
    with pytest.raises(ValueError, match='duplicate'):
        audit_scalar_cell(summary, trials, calibration)


@pytest.mark.parametrize('design,backend', [('dma', 'pipelined'), ('aes', 'transactions')])
def test_cpu_resume_preserves_completed_cells_and_rejects_vertex(tmp_path, design, backend):
    summary, trials, calibration = cell()
    out, archive = tmp_path / 'out', tmp_path / 'archive'
    directory = out / 'random/target-0.50/seed-1'
    directory.mkdir(parents=True)
    (directory / 'summary.json').write_text(json.dumps(summary))
    (directory / 'trials.jsonl').write_text('\n'.join(json.dumps(t) for t in trials))
    manifest = {'policies': ['random'], 'design': design, 'backend': backend,
                'stage': 'development', 'targets': [0.5], 'seeds': [1], 'budget': 2,
                'batch_size': 2, 'epsilon': 0.02, 'calibration': calibration}
    (out / 'manifest.json').write_text(json.dumps(manifest))
    command = [sys.executable, 'scripts/resume_cpu_panel.py', '--out', str(out), '--archive', str(archive)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert 'resumed=True' in result.stdout
    assert json.loads((archive / 'summaries.json').read_text()) == [summary]
    manifest['policies'] = ['semantic-edits-v4']
    (out / 'manifest.json').write_text(json.dumps(manifest))
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Vertex remains serial' in result.stderr


def test_panel_prepare_writes_manifest_without_trials(tmp_path):
    calibration = tmp_path / 'calibration.json'
    calibration.write_text(json.dumps({'p_min': 0, 'p_max': 1, 'epsilon_scalar': 0.02}))
    out, archive = tmp_path / 'out', tmp_path / 'archive'
    subprocess.run([sys.executable, 'scripts/run_semantic_development.py', '--prepare-only',
                    '--policies', 'random', '--calibration', str(calibration),
                    '--out', str(out), '--archive', str(archive)], check=True, capture_output=True)
    assert [p.name for p in out.iterdir()] == ['manifest.json']
    assert list(archive.iterdir()) == []
