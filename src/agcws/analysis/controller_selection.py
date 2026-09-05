"""Predeclared balanced development-AUC selection; never use held-out cells."""
from statistics import mean
import math


CANDIDATES = ('semantic-edits-v4', 'semantic-catalog-v5')


def select_controller(panels):
    if set(panels) != {(d, p) for d in ('aes', 'dma') for p in CANDIDATES}:
        raise ValueError('both candidates on both designs are required')
    conditions = {}
    models = set()
    scores = {p: {} for p in CANDIDATES}
    for (design, candidate), (manifest, rows) in panels.items():
        if manifest['design'] != design or manifest['backend'] != {'aes': 'transactions', 'dma': 'pipelined'}[design]:
            raise ValueError('design/backend mismatch')
        if manifest['stage'] != 'development' or manifest['seeds'] != [100, 101, 102]:
            raise ValueError('selection requires development seeds 100..102')
        if manifest['targets'] != [0.1, 0.25, 0.5, 0.75, 0.9] or manifest['budget'] != 50:
            raise ValueError('selection requires the complete fixed target/budget panel')
        if manifest['batch_size'] != 4 or manifest['epsilon'] != 0.02:
            raise ValueError('batch size or tolerance mismatch')
        expected = {(p, t, s) for p in manifest['policies']
                    for t in manifest['targets'] for s in manifest['seeds']}
        actual = {(r['policy'], r['target'], r['seed']) for r in rows}
        if actual != expected or len(rows) != len(expected) or candidate not in manifest['policies']:
            raise ValueError('incomplete, duplicate or missing candidate cells')
        if any(not math.isfinite(r['auc_best_so_far']) for r in rows):
            raise ValueError('nonfinite AUC')
        config = {key: manifest[key] for key in ['design', 'backend', 'batch_size', 'epsilon', 'calibration']}
        if design in conditions and conditions[design] != config:
            raise ValueError('candidate conditions differ within design')
        conditions[design] = config
        models.add(manifest['model'])
        scores[candidate][design] = mean(r['auc_best_so_far'] for r in rows if r['policy'] == candidate)
    if len(models) != 1 or None in models:
        raise ValueError('candidate comparison requires one recorded model')
    balanced = {p: mean(scores[p].values()) for p in CANDIDATES}
    selected = min(CANDIDATES, key=balanced.__getitem__)
    return {'selected_policy': selected, 'model': next(iter(models)),
            'mean_auc_by_design': scores, 'balanced_mean_auc': balanced,
            'cells_per_candidate': 30, 'tie_rule': 'v4',
            'scope': 'Development selection only; held-out performance is unproven.'}
