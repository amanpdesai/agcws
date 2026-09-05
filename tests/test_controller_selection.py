import pytest

from agcws.analysis.controller_selection import CANDIDATES, select_controller


def panels():
    result = {}
    for design in ['aes', 'dma']:
        for candidate in CANDIDATES:
            manifest = {'stage': 'development', 'design': design,
                        'backend': {'aes': 'transactions', 'dma': 'pipelined'}[design],
                        'seeds': [100, 101, 102], 'targets': [0.1, 0.25, 0.5, 0.75, 0.9],
                        'budget': 50, 'batch_size': 4, 'epsilon': 0.02, 'calibration': {},
                        'model': 'test', 'policies': [candidate]}
            rows = [{'policy': candidate, 'target': t, 'seed': s, 'auc_best_so_far': 2}
                    for t in manifest['targets'] for s in manifest['seeds']]
            result[design, candidate] = manifest, rows
    return result


def test_selection_uses_both_designs_and_ties_choose_v4():
    data = panels()
    assert select_controller(data)['selected_policy'] == CANDIDATES[0]
    for row in data['aes', CANDIDATES[1]][1]:
        row['auc_best_so_far'] = 0
    for row in data['dma', CANDIDATES[1]][1]:
        row['auc_best_so_far'] = 5
    assert select_controller(data)['selected_policy'] == CANDIDATES[0]


def test_selection_rejects_missing_cell():
    data = panels()
    data['aes', CANDIDATES[1]][1].pop()
    with pytest.raises(ValueError, match='incomplete'):
        select_controller(data)


def test_selection_rejects_held_out_seeds():
    data = panels()
    data['aes', CANDIDATES[1]][0]['seeds'] = [200, 201, 202]
    with pytest.raises(ValueError, match='development seeds'):
        select_controller(data)
