"""Apply the predeclared paired analysis to two complete held-out archives."""
import argparse
import json
from pathlib import Path

from agcws.analysis.ledger_audit import audit_scalar_cell
from agcws.analysis.semantic_comparison import compare


def load_panels(directories):
    conditions = None
    policies = set()
    combined = []
    sources = []
    for directory in directories:
        manifest = json.loads((directory / 'manifest.json').read_text())
        keys = ('stage', 'design', 'backend', 'budget', 'batch_size', 'epsilon',
                'targets', 'seeds', 'calibration', 'prompt_sha256', 'model')
        current = {key: manifest[key] for key in keys}
        if current['stage'] != 'evaluation':
            raise ValueError('development panels cannot enter held-out inference')
        if conditions is not None and current != conditions:
            raise ValueError('held-out panels have different frozen conditions')
        conditions = current
        if policies.intersection(manifest['policies']):
            raise ValueError('duplicate policy across held-out panels')
        policies.update(manifest['policies'])
        rows = json.loads((directory / 'summaries.json').read_text())
        expected = {(p, t, s) for p in manifest['policies']
                    for t in manifest['targets'] for s in manifest['seeds']}
        actual = {(r['policy'], r['target'], r['seed']) for r in rows}
        if actual != expected or len(rows) != len(expected):
            raise ValueError('incomplete or duplicate held-out panel cells')
        for row in rows:
            cell = directory / row['policy'] / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
            if not (cell / 'run_manifest.json').exists() or not (cell / 'trials.jsonl').exists():
                raise ValueError(f'missing provenance or ledger: {cell}')
            trials = [json.loads(line) for line in (cell / 'trials.jsonl').read_text().splitlines()]
            audit_scalar_cell(row, trials, manifest['calibration'])
        combined.extend(rows)
        sources.append({'archive': str(directory), 'manifest': manifest})
    if conditions is None:
        raise ValueError('at least one held-out panel is required')
    return {**conditions, 'policies': sorted(policies)}, combined, sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--aes', type=Path, nargs='+', required=True)
    parser.add_argument('--dma', type=Path, nargs='+', required=True)
    parser.add_argument('--agent', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    matrices = {}
    sources = {}
    for design, directories in [('aes', args.aes), ('dma', args.dma)]:
        manifest, rows, sources[design] = load_panels(directories)
        if manifest['design'] != design:
            raise ValueError('archive design does not match command argument')
        matrices[design] = manifest, rows
    result = {'primary_endpoint': 'AUC, lower is better',
              'difference_direction': 'agent minus baseline',
              'scope': 'Activity targeting on two designs; no equivalence claim.',
              'sources': sources,
              'comparisons': compare(matrices, args.agent)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
