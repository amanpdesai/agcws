import pytest

from agcws.analysis.semantic_comparison import compare


def matrix(design):
    policies = ['agent', 'random', 'mutation', 'evolutionary', 'scalar-edit-evolution']
    if design == 'aes':
        policies.append('coverage-guided-line')
    manifest = {'stage': 'evaluation', 'seeds': list(range(200, 210)),
                'design': design, 'backend': {'aes': 'transactions', 'dma': 'pipelined'}[design],
                'epsilon': 0.02, 'batch_size': 4,
                'targets': [0.1, 0.25, 0.5, 0.75, 0.9], 'budget': 50}
    rows = [{'policy': p, 'target': t, 'seed': s, 'auc_best_so_far': 1 if p == 'agent' else 2,
             'solved': False, 'right_censored': True, 'evaluations_to_target': 50}
            for p in policies for t in manifest['targets'] for s in manifest['seeds']]
    return manifest, rows


def test_comparison_clusters_targets_and_corrects_all_nine_tests():
    result = compare({d: matrix(d) for d in ['aes', 'dma']}, 'agent')
    assert len(result) == 9
    assert all(r['seed_differences'] == [-1] * 10 for r in result)
    assert all(r['agent_superiority'] for r in result)


def test_comparison_rejects_missing_cells():
    matrices = {d: matrix(d) for d in ['aes', 'dma']}
    matrices['aes'][1].pop()
    with pytest.raises(ValueError, match='incomplete'):
        compare(matrices, 'agent')


def test_comparison_rejects_development():
    matrices = {d: matrix(d) for d in ['aes', 'dma']}
    matrices['aes'][0]['stage'] = 'development'
    with pytest.raises(ValueError, match='evaluation'):
        compare(matrices, 'agent')


@pytest.mark.parametrize('key,value', [('backend', 'legacy'), ('epsilon', 0.05),
                                     ('batch_size', 8), ('design', 'dma')])
def test_comparison_rejects_wrong_frozen_configuration(key, value):
    matrices = {d: matrix(d) for d in ['aes', 'dma']}
    matrices['aes'][0][key] = value
    with pytest.raises(ValueError, match='backend/tolerance/batch'):
        compare(matrices, 'agent')
