"""Derive declared secondary views from audited Flash and CPU summaries."""

import argparse
import itertools
from statistics import mean

from agcws.core.storage import read, write
from agcws.evidence.flash_contract import ARM
from agcws.reporting.baselines import ARMS, DESIGNS


def derive(flash, baseline):
    result = {}
    for design in DESIGNS:
        data = flash['designs'][design]
        cells = data['cells'] + baseline['designs'][design]['cells']
        nonflat = [c for c in cells if not c['target'].endswith('flat_control')]
        slices = {str(n): {a: {
            'mean_auc': mean(sum((x+y)/2 for x, y in itertools.pairwise(c['curve'][:n]))
                             for c in nonflat if c['arm'] == a),
            'solved': sum(c['solved'] and c['evaluations_to_target'] <= n for c in nonflat if c['arm'] == a),
            'cells': sum(c['arm'] == a for c in nonflat),
        } for a in (ARM, *ARMS)} for n in (16, 32, 64, 128)}
        valid = {}
        for arm in ARMS:
            rows = [r for r in data['equal_valid_evaluations'] if r['baseline'] == arm
                    and not r['target'].endswith('flat_control')]
            eligible = [r for r in rows if r['valid_evaluations'] > 0]
            valid[arm] = {'paired_cells': len(eligible), 'zero_common_valid_cells': len(rows)-len(eligible),
                          'mean_common_valid_evaluations': mean(r['valid_evaluations'] for r in rows),
                          'flash_mean_best_error': mean(r['flash_best_error'] for r in eligible) if eligible else None,
                          'baseline_mean_best_error': mean(r['baseline_best_error'] for r in eligible) if eligible else None}
        costs = {}
        for label, rows in [('nonflat', [c for c in data['cells'] if not c['target'].endswith('flat_control')]),
                            ('all_targets', data['cells'])]:
            solved = sum(c['solved'] for c in rows)
            known = sum(c['costs']['known_usage_estimate_usd'] for c in rows)
            bound = sum(c['costs']['reconciled_conservative_liability_usd'] for c in rows)
            costs[label] = {'solves': solved, 'known_usage_subtotal_usd': known,
                            'conservative_liability_usd': bound,
                            'known_subtotal_per_solve_usd': known/solved if solved else None,
                            'conservative_liability_per_solve_usd': bound/solved if solved else None,
                            'scope': 'list-price estimates and reservations, not verified billing'}
        result[design] = {'nonflat_budget_slices': slices, 'nonflat_equal_valid_diagnostic': valid,
                          'cost_per_solve': costs}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--flash', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    write(args.output, derive(read(args.flash), read(args.baseline)))
