"""Seed-clustered inference for complete frozen semantic-search matrices."""
import math
import random
from statistics import mean

from agcws.analysis.inference import holm_bonferroni, paired_permutation_pvalue


def compare(matrices, agent):
    comparisons = []
    if set(matrices) != {'aes', 'dma'}:
        raise ValueError('both held-out designs are required')
    for design, (manifest, rows) in matrices.items():
        if manifest['stage'] != 'evaluation' or manifest['seeds'] != list(range(200, 210)):
            raise ValueError('requires frozen evaluation seeds 200..209')
        if manifest['targets'] != [0.1, 0.25, 0.5, 0.75, 0.9] or manifest['budget'] != 50:
            raise ValueError('evaluation target/budget mismatch')
        baselines = ['random', 'mutation', 'evolutionary', 'scalar-edit-evolution']
        if design == 'aes':
            baselines.append('coverage-guided-line')
        expected = {(p, t, s) for p in [agent, *baselines]
                    for t in manifest['targets'] for s in manifest['seeds']}
        indexed = {(r['policy'], r['target'], r['seed']): r for r in rows}
        if set(indexed) != expected or len(indexed) != len(rows):
            raise ValueError('incomplete, duplicate or unexpected matrix cells')
        for row in rows:
            if not math.isfinite(row['auc_best_so_far']):
                raise ValueError('nonfinite AUC')
            if not row['solved'] and (not row['right_censored'] or row['evaluations_to_target'] != 50):
                raise ValueError('invalid censoring')
        for baseline in baselines:
            differences = [mean(indexed[agent, t, s]['auc_best_so_far'] -
                                indexed[baseline, t, s]['auc_best_so_far']
                                for t in manifest['targets']) for s in manifest['seeds']]
            rng = random.Random(0)
            boot = sorted(mean(rng.choices(differences, k=10)) for _ in range(10000))
            comparisons.append({'design': design, 'baseline': baseline, 'agent': agent,
                                'mean_auc_difference': mean(differences),
                                'seed_differences': differences,
                                'bootstrap_95_interval': [boot[249], boot[9749]],
                                'p_value': paired_permutation_pvalue(differences, [0] * 10)})
    for row, adjusted in zip(comparisons, holm_bonferroni(r['p_value'] for r in comparisons)):
        row['holm_p_value'] = adjusted
        row['agent_superiority'] = row['mean_auc_difference'] < 0 and adjusted < 0.05
    return comparisons
