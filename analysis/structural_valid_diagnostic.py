"""Conditional equal-valid-evaluation diagnostic for the frozen temporal panel."""
import argparse
import json
from pathlib import Path
from statistics import mean

from analysis.valid_evaluation_diagnostic import mean_auc, valid_curve
from validation.aes_gls import sha


def build(root):
    report_path = root/'heldout.json'
    report = json.loads(report_path.read_text())
    curves, hashes = {}, {}
    for name, digest in report['artifact_sha256'].items():
        if not name.endswith('/trials.jsonl'):
            continue
        path = root/name
        if sha(path) != digest:
            raise ValueError('changed ledger')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if len(rows) != 32:
            raise ValueError('incomplete ledger')
        design, target, seed, policy, _ = Path(name).parts
        key = (design, target, seed, policy)
        if key in curves:
            raise ValueError('duplicate cell')
        curves[key] = valid_curve(rows)
        hashes[name] = digest
    if len(curves) != 160:
        raise ValueError('incomplete panel')
    comparisons = []
    for design in ('aes', 'dma'):
        for method in ('edit-agent', 'edit-hybrid'):
            for baseline in ('random', 'evolutionary'):
                for k in (8, 16, 24, 32):
                    pairs, excluded = [], []
                    for target in report['spec']['targets']:
                        for seed in report['spec']['seeds']:
                            left = curves[design, target, f'seed-{seed}', method]
                            right = curves[design, target, f'seed-{seed}', baseline]
                            identity = {'target': target, 'seed': seed, 'method_valid': len(left), 'baseline_valid': len(right)}
                            if min(len(left), len(right)) < k:
                                excluded.append(identity)
                            else:
                                pairs.append({**identity, 'method_mean_error': mean_auc(left,k),
                                              'baseline_mean_error': mean_auc(right,k)})
                    comparisons.append({'design': design, 'method': method, 'baseline': baseline,
                                        'valid_budget': k, 'matched_cells': len(pairs), 'total_cells': 20,
                                        'method_mean_error': mean(p['method_mean_error'] for p in pairs) if pairs else None,
                                        'baseline_mean_error': mean(p['baseline_mean_error'] for p in pairs) if pairs else None,
                                        'pairs': pairs, 'excluded': excluded})
    return {'scope': 'Post-hoc descriptive diagnostic; original proposal-counted inference unchanged.',
            'endpoint': 'Trapezoidal best-so-far loss AUC over first K valid evaluations divided by K-1.',
            'limitations': ['Conditional on both methods reaching K valid outputs within 32 slots.',
                            'Exclusion can select easier cells; invalid outputs still affected adaptive history.',
                            'Not a causal estimate of schema-compliance effects; no new significance tests.'],
            'source_sha256': sha(report_path), 'ledger_sha256': hashes, 'comparisons': comparisons}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('results/structural_temporal_heldout_v1'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.root)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
