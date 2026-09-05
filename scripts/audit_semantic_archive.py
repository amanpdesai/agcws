"""Audit completed cells in an incremental development or evaluation archive."""
import argparse
import json
from pathlib import Path

from agcws.analysis.ledger_audit import audit_scalar_cell


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.archive / 'manifest.json').read_text())
    rows = json.loads((args.archive / 'summaries.json').read_text())
    slots = 0
    for row in rows:
        cell = args.archive / row['policy'] / f"target-{row['target']:.2f}" / f"seed-{row['seed']}"
        trials = [json.loads(line) for line in (cell / 'trials.jsonl').read_text().splitlines()]
        slots += audit_scalar_cell(row, trials, manifest['calibration'])['audited_slots']
    print(json.dumps({'audited_cells': len(rows), 'audited_slots': slots,
                      'expected_cells': len(manifest['policies']) * len(manifest['seeds']) * len(manifest['targets']),
                      'stage': manifest['stage']}))


if __name__ == '__main__':
    main()
