"""Apply the predeclared paired analysis to two complete held-out archives."""
import argparse
import json
from pathlib import Path

from agcws.analysis.semantic_comparison import compare


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--aes', type=Path, required=True)
    parser.add_argument('--dma', type=Path, required=True)
    parser.add_argument('--agent', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    matrices = {}
    for design, directory in [('aes', args.aes), ('dma', args.dma)]:
        manifest = json.loads((directory / 'manifest.json').read_text())
        rows = json.loads((directory / 'summaries.json').read_text())
        for row in rows:
            cell = directory / row['policy'] / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
            if not (cell / 'run_manifest.json').exists() or not (cell / 'trials.jsonl').exists():
                raise ValueError(f'missing provenance or ledger: {cell}')
        matrices[design] = manifest, rows
    result = {'primary_endpoint': 'AUC, lower is better',
              'difference_direction': 'agent minus baseline',
              'scope': 'Activity targeting on two designs; no equivalence claim.',
              'comparisons': compare(matrices, args.agent)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
