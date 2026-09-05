"""Combine complete development panels with matching experimental conditions."""
import argparse
import json
from pathlib import Path
from statistics import mean

from agcws.analysis.ledger_audit import audit_scalar_cell


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archives', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    conditions = None
    rows = []
    policies = set()
    sources = []
    for archive in args.archives:
        manifest = json.loads((archive / 'manifest.json').read_text())
        selected = {key: manifest[key] for key in
                    ['stage', 'design', 'backend', 'budget', 'batch_size', 'epsilon',
                     'targets', 'seeds', 'calibration']}
        if selected['stage'] != 'development':
            raise ValueError('use the predeclared inference command for held-out evaluation')
        if conditions is not None and selected != conditions:
            raise ValueError('panels have different experimental conditions')
        conditions = selected
        if policies.intersection(manifest['policies']):
            raise ValueError('duplicate policy across panels')
        policies.update(manifest['policies'])
        panel = json.loads((archive / 'summaries.json').read_text())
        expected = {(p, t, s) for p in manifest['policies']
                    for t in manifest['targets'] for s in manifest['seeds']}
        actual = {(r['policy'], r['target'], r['seed']) for r in panel}
        if actual != expected or len(panel) != len(expected):
            raise ValueError(f'incomplete or duplicate cells: {archive}')
        for row in panel:
            cell = archive / row['policy'] / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
            trials = [json.loads(line) for line in (cell / 'trials.jsonl').read_text().splitlines()]
            audit_scalar_cell(row, trials, manifest['calibration'])
        rows.extend(panel)
        sources.append({'archive': str(archive), 'manifest': manifest})
    aggregate = []
    for policy in sorted(policies):
        subset = [r for r in rows if r['policy'] == policy]
        aggregate.append({'policy': policy, 'runs': len(subset),
                          'mean_auc': mean(r['auc_best_so_far'] for r in subset),
                          'solve_rate': mean(r['solved'] for r in subset),
                          'valid_fraction': sum(r['valid_trials'] for r in subset) / sum(r['budget'] for r in subset),
                          'est_cost_usd': sum(r['est_cost_usd'] for r in subset),
                          'unknown_usage_batches': sum(r.get('unknown_usage_batches', 0) for r in subset)})
    output = {'conditions': conditions, 'sources': sources,
              'scope': 'Complete development panels; descriptive only, not held-out evidence.',
              'primary_endpoint': 'mean_auc_lower_is_better',
              'policies': sorted(aggregate, key=lambda r: r['mean_auc'])}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output['policies'], indent=2))


if __name__ == '__main__':
    main()
