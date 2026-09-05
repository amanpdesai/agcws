import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    'evaluation_panels', Path(__file__).parents[1] / 'scripts/compare_semantic_evaluation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def panel(root, policy, **changes):
    directory = root / policy
    directory.mkdir()
    manifest = {'stage': 'evaluation', 'design': 'aes', 'backend': 'transactions',
                    'budget': 50, 'batch_size': 4, 'epsilon': 0.02, 'targets': [0.1], 'seeds': [200],
                    'calibration': {}, 'prompt_sha256': 'frozen', 'model': 'test', 'policies': [policy]}
    manifest.update(changes)
    (directory / 'manifest.json').write_text(json.dumps(manifest))
    row = {'policy': policy, 'target': 0.1, 'seed': 200}
    (directory / 'summaries.json').write_text(json.dumps([row]))
    cell = directory / policy / 'target-0.10' / 'seed-200'
    cell.mkdir(parents=True)
    (cell / 'trials.jsonl').write_text('{}\n')
    (cell / 'run_manifest.json').write_text('{}')
    return directory


def test_merges_disjoint_panels_and_audits_each_ledger(tmp_path, monkeypatch):
    audited = []
    monkeypatch.setattr(module, 'audit_scalar_cell', lambda *args: audited.append(args))
    manifest, rows, sources = module.load_panels(
        [panel(tmp_path, 'random'), panel(tmp_path, 'agent')])
    assert manifest['policies'] == ['agent', 'random']
    assert len(rows) == len(sources) == len(audited) == 2


@pytest.mark.parametrize('changes', [{'epsilon': 0.05}, {'model': 'different'},
                                    {'prompt_sha256': 'changed'}])
def test_rejects_changed_conditions(tmp_path, monkeypatch, changes):
    monkeypatch.setattr(module, 'audit_scalar_cell', lambda *args: None)
    with pytest.raises(ValueError, match='different frozen conditions'):
        module.load_panels([panel(tmp_path, 'random'), panel(tmp_path, 'agent', **changes)])


def test_rejects_missing_cells_and_development(tmp_path):
    archive = panel(tmp_path, 'random')
    (archive / 'summaries.json').write_text('[]')
    with pytest.raises(ValueError, match='incomplete'):
        module.load_panels([archive])
    with pytest.raises(ValueError, match='development'):
        module.load_panels([panel(tmp_path, 'agent', stage='development')])


def test_rejects_missing_provenance(tmp_path):
    archive = panel(tmp_path, 'random')
    (archive / 'random/target-0.10/seed-200/run_manifest.json').unlink()
    with pytest.raises(ValueError, match='missing provenance'):
        module.load_panels([archive])
