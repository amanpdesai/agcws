import json
from copy import deepcopy

import pytest

from analysis.report_semantic_evaluation import build_report, describe, verify_manifest


def test_descriptive_retains_unsolved_and_unknown_cost():
    row = {'policy': 'agent', 'auc_best_so_far': 2.0, 'solved': False,
           'evaluations_to_target': 50, 'right_censored': True,
           'proposal_slots': 50, 'valid_trials': 40,
           'validity_failures': {'SCHEMA': 10}, 'unknown_usage_batches': 1,
           'tokens_in': 100, 'tokens_out': 50, 'est_cost_usd': 0.01}
    result = describe([row])[0]
    assert result['mean_auc_best_so_far'] == 2
    assert result['mean_capped_evaluations_to_target'] == 50
    assert result['solve_rate'] == 0
    assert result['validity_rate'] == 0.8
    assert not result['cost_accounting_complete']
    row['valid_trials'] = 41
    with pytest.raises(ValueError, match='partition'):
        describe([row])


def fixture_manifest():
    fields = ('source_digest source_hashes adapter schema_sha256 budget batch_size '
              'p_min p_max useful_work_floor python packages pricing model prompt_hash sampling')
    template = dict.fromkeys(fields.split(), 'fixed')
    template['goal'] = {'q': 0.5, 'tolerance': 0.02}
    actual = deepcopy(template)
    actual.update(goal={'q': 0.1, 'tolerance': 0.02}, seed=200, policy='agent')
    return actual, template, {'target': 0.1, 'seed': 200, 'policy': 'agent'}


@pytest.mark.parametrize('field', ['source_digest', 'source_hashes', 'model',
                                  'prompt_hash', 'sampling', 'p_min', 'useful_work_floor'])
def test_manifest_rejects_freeze_drift(field):
    actual, template, row = fixture_manifest()
    verify_manifest(actual, template, row, 'agent')
    actual[field] = 'changed'
    with pytest.raises(ValueError, match=field):
        verify_manifest(actual, template, row, 'agent')


def test_manifest_rejects_wrong_goal_and_allows_cpu_without_model():
    actual, template, row = fixture_manifest()
    actual['goal']['tolerance'] = 0.05
    with pytest.raises(ValueError, match='identity/goal'):
        verify_manifest(actual, template, row, 'agent')
    actual['goal']['tolerance'] = 0.02
    actual['policy'] = row['policy'] = 'random'
    actual['model'] = actual['prompt_hash'] = None
    verify_manifest(actual, template, row, 'agent')


def test_report_end_to_end_complete_grid_and_corrupt_inputs(tmp_path):
    targets, seeds = [0.1, 0.25, 0.5, 0.75, 0.9], list(range(200, 210))
    _, template, _ = fixture_manifest()
    template.update(budget=50, batch_size=4, p_min=0, p_max=10, useful_work_floor=38)
    freeze = tmp_path / 'freeze.json'
    freeze.write_text(json.dumps({'selected_policy': 'agent',
                                  'configuration_templates': dict.fromkeys(['aes', 'dma'], template)}))
    panels = {}
    for design in ['aes', 'dma']:
        directory = tmp_path / design
        directory.mkdir()
        panels[design] = [directory]
        policies = ['agent', 'random', 'mutation', 'evolutionary', 'scalar-edit-evolution']
        if design == 'aes':
            policies.append('coverage-guided-line')
        calibration = {'p_min': 0, 'p_max': 10, 'useful_work_floor': 38}
        manifest = {'stage': 'evaluation', 'design': design,
                    'backend': 'transactions' if design == 'aes' else 'pipelined',
                    'budget': 50, 'batch_size': 4, 'epsilon': 0.02,
                    'targets': targets, 'seeds': seeds, 'policies': policies,
                    'calibration': calibration, 'prompt_sha256': 'fixed', 'model': 'fixed'}
        (directory / 'manifest.json').write_text(json.dumps(manifest))
        rows = []
        for policy in policies:
            for target in targets:
                for seed in seeds:
                    goal = {'q': target, 'tolerance': 0.02}
                    row = {'policy': policy, 'target': target, 'seed': seed,
                           'epsilon': 0.02, 'budget': 50, 'auc_best_so_far': 0,
                           'solved': True, 'right_censored': False,
                           'evaluations_to_target': 1, 'proposal_slots': 50,
                           'valid_trials': 50, 'validity_failures': {},
                           'unknown_usage_batches': 0, 'tokens_in': 0,
                           'tokens_out': 0, 'est_cost_usd': 0}
                    rows.append(row)
                    cell = directory / policy / f'target-{target:.2f}' / f'seed-{seed}'
                    cell.mkdir(parents=True)
                    run = {**template, 'policy': policy, 'seed': seed, 'goal': goal}
                    (cell / 'run_manifest.json').write_text(json.dumps(run))
                    trial = {'policy': policy, 'seed': seed, 'goal': goal,
                             'validity': {'valid': True}, 'loss': 0,
                             'profile': {'mean_power': target * 10, 'useful_work': 38, 'valid': True},
                             'tokens_in': 0, 'tokens_out': 0, 'est_cost_usd': 0}
                    (cell / 'trials.jsonl').write_text('\n'.join(
                        json.dumps({**trial, 'trial_id': str(i)}) for i in range(50)))
        (directory / 'summaries.json').write_text(json.dumps(rows))
    result = build_report(panels, freeze)
    assert len(result['comparisons']) == 9
    assert not any(r['agent_superiority'] for r in result['comparisons'])
    assert all(r['cells'] == 50 for rows in result['descriptive'].values() for r in rows)
    assert len(result['artifact_sha256']) == 1104
    cell = panels['aes'][0] / 'agent/target-0.10/seed-200/run_manifest.json'
    original = cell.read_text()
    corrupted = json.loads(original)
    corrupted['source_digest'] = 'unfrozen'
    cell.write_text(json.dumps(corrupted))
    with pytest.raises(ValueError, match='source_digest'):
        build_report(panels, freeze)
    cell.write_text(original)
    summaries = panels['dma'][0] / 'summaries.json'
    summaries.write_text(json.dumps(json.loads(summaries.read_text())[:-1]))
    with pytest.raises(ValueError, match='incomplete'):
        build_report(panels, freeze)
