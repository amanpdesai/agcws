"""Summarize complete paired development cells without dropping failed searches."""
import argparse
import json
from pathlib import Path
from statistics import mean


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.archive / 'manifest.json').read_text())
    rows = json.loads((args.archive / 'summaries.json').read_text())
    expected = {(p, t, s) for p in manifest['policies']
                for t in manifest['targets'] for s in manifest['seeds']}
    keys = {(r['policy'], r['target'], r['seed']) for r in rows}
    if len(keys) != len(rows) or keys != expected:
        raise ValueError(f'incomplete or duplicate matrix: {len(keys)}/{len(expected)} cells')
    for row in rows:
        if not row['solved'] and (row['evaluations_to_target'] != manifest['budget']
                                  or not row['right_censored']):
            raise ValueError('invalid censoring')
    aggregate = []
    for policy in manifest['policies']:
        subset = [r for r in rows if r['policy'] == policy]
        aggregate.append({'policy': policy, 'runs': len(subset),
                          'mean_auc': mean(r['auc_best_so_far'] for r in subset),
                          'solve_rate': mean(r['solved'] for r in subset),
                          'valid_fraction': sum(r['valid_trials'] for r in subset) /
                                            sum(r['proposal_slots'] for r in subset),
                          'est_cost_usd': sum(r['est_cost_usd'] for r in subset)})
    output = {'stage': manifest['stage'], 'complete': True,
              'primary_endpoint': 'mean_auc_lower_is_better', 'policies': aggregate,
              'scope': 'Development results; no confirmatory inference or parity claim.'}
    (args.archive / 'aggregate.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
