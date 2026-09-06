"""Seed-clustered temporal inference, separate from development selection."""
import math
import random
from statistics import mean

from agcws.analysis.inference import holm_bonferroni, paired_permutation_pvalue


def compare(rows, spec):
    if spec['phase'] != 'held-out' or spec['seeds'] != list(range(400, 410)):
        raise ValueError('requires fresh temporal held-out seeds 400..409')
    if spec['designs'] != ['aes', 'dma'] or spec['targets'] != ['random_300', 'random_301']:
        raise ValueError('unexpected temporal task panel')
    if spec['budget'] != 32 or spec['batch_size'] != 4:
        raise ValueError('unexpected temporal budget')
    families = {
        'best-eight': ('evolutionary', 'edit-agent', 'edit-hybrid'),
        'peak-window-population': ('population-evolution', 'population-agent', 'population-hybrid'),
    }
    cpu, agent, hybrid = families[spec['selected_family']]
    policies = ['random', cpu, agent, hybrid]
    if set(spec['policies']) != set(policies) or len(spec['policies']) != 4:
        raise ValueError('unexpected policy panel')
    expected = {(d, t, s, p) for d in spec['designs'] for t in spec['targets']
                for s in spec['seeds'] for p in policies}
    indexed = {(r['design_key'], r['reference_name'], r['seed'], r['policy_alias']): r for r in rows}
    if set(indexed) != expected or len(indexed) != len(rows):
        raise ValueError('missing, duplicate or unexpected cells')
    for row in rows:
        if not math.isfinite(row['auc_best_so_far']):
            raise ValueError('nonfinite AUC')
        if (row['right_censored'] != (not row['solved'])
                or not 1 <= row['evaluations_to_target'] <= spec['budget']
                or (not row['solved'] and row['evaluations_to_target'] != spec['budget'])):
            raise ValueError('incorrect right censoring')
    comparisons = []
    for design in spec['designs']:
        for method in (agent, hybrid):
            for baseline in ('random', cpu):
                differences = [mean(
                    indexed[design, target, seed, method]['auc_best_so_far']
                    - indexed[design, target, seed, baseline]['auc_best_so_far']
                    for target in spec['targets']) for seed in spec['seeds']]
                rng = random.Random(0)
                boot = sorted(mean(rng.choices(differences, k=10)) for _ in range(10000))
                comparisons.append({
                    'design': design, 'method': method, 'baseline': baseline,
                    'seed_differences': differences, 'mean_auc_difference': mean(differences),
                    'pointwise_bootstrap_95_interval': [boot[249], boot[9749]],
                    'p_value': paired_permutation_pvalue(differences, [0.0] * 10),
                })
    for row, adjusted in zip(comparisons, holm_bonferroni(r['p_value'] for r in comparisons)):
        row['holm_p_value'] = adjusted
        row['superiority_supported'] = row['mean_auc_difference'] < 0 and adjusted < 0.05
    return {'scope': 'Matched-work/window activity targeting on observed reference tasks, fresh search seeds.',
            'primary_endpoint': 'Proposal-counted best-so-far loss AUC, lower is better.',
            'unit': 'Ten seed units; two target differences averaged within each seed.',
            'multiplicity': 'Joint Holm correction over eight method/baseline/design tests.',
            'claim_limit': 'Nonsignificance is not equivalence; target-profile generalization and gate-power prediction are not tested.',
            'comparisons': comparisons}
