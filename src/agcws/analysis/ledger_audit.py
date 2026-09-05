"""Recompute scalar endpoints from archived measurements, not summary claims."""
import math


def audit_scalar_cell(summary, trials, calibration):
    budget = summary['budget']
    if len(trials) != budget or len({t['trial_id'] for t in trials}) != budget:
        raise ValueError('incomplete or duplicate trial ledger')
    lo, hi = calibration['p_min'], calibration['p_max']
    if not hi > lo:
        raise ValueError('invalid calibration envelope')
    best = math.inf
    curve = []
    solved_at = None
    valid_count = 0
    for index, trial in enumerate(trials, 1):
        if (trial['policy'], trial['seed'], trial['goal']) != (
                summary['policy'], summary['seed'],
                {'q': summary['target'], 'tolerance': summary['epsilon']}):
            raise ValueError('trial configuration mismatch')
        if trial['validity']['valid']:
            valid_count += 1
            profile = trial['profile']
            if not profile['valid'] or profile['useful_work'] < calibration['useful_work_floor']:
                raise ValueError('valid trial violates useful-work/profile gate')
            measured = abs((profile['mean_power'] - lo) / (hi - lo) - summary['target'])
            if not math.isfinite(measured) or not math.isclose(measured, trial['loss'], rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError('loss disagrees with measured activity and calibration')
            best = min(best, measured)
        elif trial['loss'] is not None:
            raise ValueError('invalid trial has a scored loss')
        curve.append(best if math.isfinite(best) else 1.0)
        if solved_at is None and best <= summary['epsilon']:
            solved_at = index
    auc = sum((a + b) / 2 for a, b in zip(curve, curve[1:]))
    if not math.isclose(auc, summary['auc_best_so_far'], rel_tol=1e-10, abs_tol=1e-12):
        raise ValueError('summary AUC disagrees with ledger')
    if (summary['solved'], summary['right_censored'], summary['evaluations_to_target']) != (
            solved_at is not None, solved_at is None, solved_at or budget):
        raise ValueError('summary censoring disagrees with ledger')
    if summary['valid_trials'] != valid_count:
        raise ValueError('summary validity count disagrees with ledger')
    for field in ['tokens_in', 'tokens_out', 'est_cost_usd']:
        if not math.isclose(sum(t[field] for t in trials), summary[field], rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError(f'summary {field} disagrees with ledger')
    return {'audited_slots': budget, 'auc': auc, 'solved': solved_at is not None}
