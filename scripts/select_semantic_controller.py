"""Audit all candidate panels before selecting one cross-design controller."""
import argparse
import hashlib
import json
from pathlib import Path

from agcws.analysis.controller_selection import CANDIDATES, select_controller
from agcws.analysis.ledger_audit import audit_scalar_cell


def main():
    parser = argparse.ArgumentParser()
    for design in ['aes', 'dma']:
        for version in ['v4', 'v5']:
            parser.add_argument(f'--{design}-{version}', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    panels, provenance = {}, []
    for design in ['aes', 'dma']:
        for version, candidate in zip(['v4', 'v5'], CANDIDATES):
            archive = getattr(args, f'{design}_{version}')
            manifest = json.loads((archive / 'manifest.json').read_text())
            rows = json.loads((archive / 'summaries.json').read_text())
            for row in rows:
                cell = archive / row['policy'] / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
                trials = [json.loads(line) for line in (cell / 'trials.jsonl').read_text().splitlines()]
                audit_scalar_cell(row, trials, manifest['calibration'])
            panels[design, candidate] = manifest, rows
            provenance.append({'archive': str(archive), 'manifest': manifest,
                               'summaries_sha256': hashlib.sha256((archive / 'summaries.json').read_bytes()).hexdigest()})
    selection = select_controller(panels)
    selection['sources'] = provenance
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise ValueError('selection already exists; do not overwrite a recorded decision')
    args.out.write_text(json.dumps(selection, indent=2) + '\n')
    print(json.dumps({k: v for k, v in selection.items() if k != 'sources'}, indent=2))


if __name__ == '__main__':
    main()
