import itertools

import pytest

from analysis.structural_inference import compare


def panel():
    spec = {'phase': 'held-out', 'designs': ['aes', 'dma'],
            'targets': ['random_300', 'random_301'], 'seeds': list(range(400, 410)),
            'budget': 32, 'batch_size': 4, 'selected_family': 'best-eight',
            'policies': ['random', 'evolutionary', 'edit-agent', 'edit-hybrid']}
    rows = [{'design_key': d, 'reference_name': t, 'seed': s, 'policy_alias': p,
             'auc_best_so_far': 1.0, 'solved': False, 'right_censored': True,
             'evaluations_to_target': 32}
            for d, t, s, p in itertools.product(spec['designs'], spec['targets'],
                                               spec['seeds'], spec['policies'])]
    return spec, rows


def test_equal_methods_are_not_declared_superior():
    spec, rows = panel()
    result = compare(rows, spec)
    assert len(result['comparisons']) == 8
    assert all(r['holm_p_value'] == 1 and not r['superiority_supported']
               and r['pointwise_bootstrap_95_interval'] == [0, 0] for r in result['comparisons'])


def test_ten_seed_units_not_twenty_targets():
    spec, rows = panel()
    for row in rows:
        if row['policy_alias'] in ('edit-agent', 'edit-hybrid'):
            row['auc_best_so_far'] = 0.5
    result = compare(rows, spec)
    assert all(len(r['seed_differences']) == 10 and r['superiority_supported']
               for r in result['comparisons'])
    assert result['comparisons'][0]['holm_p_value'] == pytest.approx(8 * 2 / 1024)


@pytest.mark.parametrize('corruption', ['missing', 'duplicate', 'censoring', 'seed'])
def test_incomplete_or_corrupt_panel_rejected(corruption):
    spec, rows = panel()
    if corruption == 'missing':
        rows.pop()
    elif corruption == 'duplicate':
        rows.append(rows[0])
    elif corruption == 'censoring':
        rows[0]['evaluations_to_target'] = 0
    else:
        rows[0]['seed'] = 310
    with pytest.raises(ValueError):
        compare(rows, spec)
