"""Frozen-manifest audit and complete-panel descriptive/inferential report."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean

from agcws.analysis.semantic_comparison import compare
from scripts.compare_semantic_evaluation import load_panels


def verify_manifest(actual, template, row, agent):
    keys = ('source_digest', 'source_hashes', 'adapter', 'schema_sha256',
            'budget', 'batch_size', 'p_min', 'p_max', 'useful_work_floor',
            'python', 'packages', 'pricing')
    if row['policy'] == agent:
        keys += ('model', 'prompt_hash', 'sampling')
    for key in keys:
        if actual[key] != template[key]:
            raise ValueError(f'frozen manifest mismatch: {key}')
    goal = {**template['goal'], 'q': row['target']}
    if (actual['goal'] != goal or actual['seed'] != row['seed']
            or actual['policy'] != row['policy']):
        raise ValueError('cell identity/goal mismatch')


def describe(rows):
    output = []
    for policy in sorted({r['policy'] for r in rows}):
        cells = [r for r in rows if r['policy'] == policy]
        failures = Counter()
        for row in cells:
            failures.update(row['validity_failures'])
        slots = sum(r['proposal_slots'] for r in cells)
        valid = sum(r['valid_trials'] for r in cells)
        if sum(failures.values()) + valid != slots:
            raise ValueError('validity stages do not partition proposal slots')
        unknown = sum(r['unknown_usage_batches'] for r in cells)
        output.append({
            'policy': policy,
            'mean_auc_best_so_far': mean(r['auc_best_so_far'] for r in cells),
            'cells': len(cells),
            'solve_rate': mean(r['solved'] for r in cells),
            'mean_capped_evaluations_to_target': mean(r['evaluations_to_target'] for r in cells),
            'right_censored_runs': sum(r['right_censored'] for r in cells),
            'proposal_slots': slots, 'valid_trials': valid,
            'validity_rate': valid / slots, 'validity_failures': dict(failures),
            'tokens_in': sum(r['tokens_in'] for r in cells),
            'tokens_out': sum(r['tokens_out'] for r in cells),
            'est_cost_usd': sum(r['est_cost_usd'] for r in cells),
            'unknown_usage_batches': unknown, 'cost_accounting_complete': unknown == 0,
        })
    return output


def build_report(panels, freeze_path):
    frozen_bytes = freeze_path.read_bytes()
    freeze = json.loads(frozen_bytes)
    agent = freeze['selected_policy']
    matrices, sources, descriptions, checksums = {}, {}, {}, {}
    for design, directories in panels.items():
        manifest, rows, sources[design] = load_panels(directories)
        template = freeze['configuration_templates'][design]
        for directory in directories:
            local_rows = json.loads((directory / 'summaries.json').read_text())
            for row in local_rows:
                cell = directory / row['policy'] / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
                verify_manifest(json.loads((cell / 'run_manifest.json').read_text()),
                                template, row, agent)
            for path in sorted(directory.rglob('*')):
                if path.is_file() and path.suffix in ('.json', '.jsonl'):
                    checksums[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        matrices[design] = manifest, rows
        descriptions[design] = describe(rows)
    comparisons = compare(matrices, agent)
    return {
        'primary_endpoint': 'AUC of best-so-far error; lower is better',
        'scope': 'Held-out scalar activity targeting, not power or structural expressiveness.',
        'censoring': 'Unsolved runs contribute 50 to capped evaluations-to-target; not a mean completion time.',
        'cost_note': 'Configured-rate estimates; unknown usage makes totals incomplete.',
        'freeze_sha256': hashlib.sha256(frozen_bytes).hexdigest(),
        'descriptive': descriptions, 'comparisons': comparisons,
        'sources': sources, 'artifact_sha256': checksums,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--aes', type=Path, nargs='+', required=True)
    parser.add_argument('--dma', type=Path, nargs='+', required=True)
    parser.add_argument('--freeze', type=Path, default=Path('results/semantic_evaluation_freeze.json'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = build_report({'aes': args.aes, 'dma': args.dma}, args.freeze)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        stream.write(json.dumps(report, indent=2) + '\n')
    print(f'Complete audited report: {args.out}')


if __name__ == '__main__':
    main()
