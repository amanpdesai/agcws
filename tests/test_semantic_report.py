from copy import deepcopy

import pytest

from analysis.report_semantic_evaluation import describe, verify_manifest


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
