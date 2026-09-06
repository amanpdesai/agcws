"""Post-hoc valid-evaluation curves; never replaces proposal-counted inference."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean


def valid_curve(rows):
    curve = []
    best = math.inf
    for row in rows:
        if row['validity']['valid']:
            loss = row['loss']
            if loss is None or not math.isfinite(loss) or loss < 0:
                raise ValueError('valid trial has invalid loss')
            best = min(best, loss)
            curve.append(best)
    return curve


def mean_auc(curve, k):
    if k < 2 or len(curve) < k:
        raise ValueError('insufficient valid evaluations')
    return sum((curve[i - 1] + curve[i]) / 2 for i in range(1, k)) / (k - 1)


def build(report_path):
    data = report_path.read_bytes()
    report = json.loads(data)
    panels = {}
    hashes = {}
    for name, digest in report['artifact_sha256'].items():
        if not name.endswith('/trials.jsonl'):
            continue
        raw = Path(name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f'archived ledger changed: {name}')
        hashes[name] = digest
        rows = [json.loads(line) for line in raw.splitlines()]
        if len(rows) != 50:
            raise ValueError(f'incomplete ledger: {name}')
        first = rows[0]
        identity = (first['design'], first['policy'], first['seed'], first['goal']['q'])
        if any((r['design'], r['policy'], r['seed'], r['goal']['q']) != identity for r in rows):
            raise ValueError('mixed cell identity')
        if identity in panels:
            raise ValueError('duplicate cell')
        panels[identity] = valid_curve(rows)
    agent = 'semantic-edits-v4'
    output = []
    for design in sorted({key[0] for key in panels}):
        policies = sorted({key[1] for key in panels if key[0] == design} - {agent})
        instances = sorted((key[2], key[3]) for key in panels
                           if key[:2] == (design, agent))
        for baseline in policies:
            for k in (10, 20, 30, 40, 50):
                pairs, excluded = [], []
                for seed, target in instances:
                    left = panels[design, agent, seed, target]
                    right = panels[design, baseline, seed, target]
                    if min(len(left), len(right)) < k:
                        excluded.append({'seed': seed, 'target': target,
                                         'agent_valid': len(left), 'baseline_valid': len(right)})
                        continue
                    pairs.append({'seed': seed, 'target': target,
                                  'agent_mean_auc': mean_auc(left, k),
                                  'baseline_mean_auc': mean_auc(right, k),
                                  'agent_solved': left[k - 1] <= 0.02,
                                  'baseline_solved': right[k - 1] <= 0.02})
                output.append({
                    'design': design, 'baseline': baseline, 'valid_budget': k,
                    'matched_cells': len(pairs), 'total_cells': len(instances),
                    'agent_mean_auc': mean(p['agent_mean_auc'] for p in pairs) if pairs else None,
                    'baseline_mean_auc': mean(p['baseline_mean_auc'] for p in pairs) if pairs else None,
                    'agent_solve_rate': mean(p['agent_solved'] for p in pairs) if pairs else None,
                    'baseline_solve_rate': mean(p['baseline_solved'] for p in pairs) if pairs else None,
                    'pairs': pairs, 'excluded': excluded,
                })
    return {
        'scope': 'Post-hoc descriptive diagnostic, not new confirmatory inference or a rerun.',
        'endpoint': 'Trapezoidal best-so-far loss AUC over valid indices 1..K, divided by K-1.',
        'limitations': [
            'Conditional on both policies reaching K valid evaluations within 50 proposed slots.',
            'Incomplete support is reported, not imputed; compare policies only within each matched pair panel.',
            'Invalid proposals affected adaptive histories and cost; filtering cannot isolate a causal compliance effect.',
            'Primary proposal-counted AUC and its frozen inference remain unchanged.',
        ],
        'source_report_sha256': hashlib.sha256(data).hexdigest(),
        'ledger_sha256': hashes, 'comparisons': output,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, default=Path('results/semantic_heldout_comparison.json'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.report)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
