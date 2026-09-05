"""Archive existing run manifests; never reconstruct missing provenance."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    copied = missing = 0
    for row in json.loads((args.archive / 'summaries.json').read_text()):
        relative = Path(row['policy']) / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
        source = args.source / relative / 'run_manifest.json'
        if not source.exists():
            missing += 1
            continue
        record = json.loads(source.read_text())
        if (record['policy'], record['seed'], record['budget'], record['goal']) != (
                row['policy'], row['seed'], row['budget'],
                {'q': row['target'], 'tolerance': row['epsilon']}):
            raise ValueError(f'run manifest does not match archived cell: {source}')
        target = args.archive / relative / 'run_manifest.json'
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError(f'conflicting existing manifest: {target}')
        target.write_bytes(source.read_bytes())
        copied += 1
    print(json.dumps({'copied': copied, 'missing_not_reconstructed': missing}))


if __name__ == '__main__':
    main()
