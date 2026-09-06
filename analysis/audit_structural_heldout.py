"""Audit every frozen temporal cell before archiving held-out inference."""
import argparse
import hashlib
import itertools
import json
import shutil
from pathlib import Path

from agcws.experiments.freeze import verify_frozen_manifest
from analysis.audit_structural_panel import FILES, audit_cell, require
from analysis.structural_inference import compare


def build(source, freeze_path):
    raw = freeze_path.read_bytes()
    frozen = json.loads(raw)
    spec = frozen['spec']
    rows, hashes = [], {}
    corpora = {}
    for design, record in frozen['corpora'].items():
        data = Path(record['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record['sha256'], 'frozen corpus changed')
        corpora[design] = json.loads(data)
    for design, target, seed, policy in itertools.product(
            spec['designs'], spec['targets'], spec['seeds'], spec['policies']):
        relative = Path(design) / target / f'seed-{seed}' / policy
        row, actual, reference = audit_cell(source / relative, design, target, seed, policy, spec['budget'])
        require(reference['phase'] == 'held-out', 'cell is not labeled held-out')
        require(reference.get('freeze_sha256') == hashlib.sha256(raw).hexdigest(), 'cell freeze mismatch')
        require(reference['source_sha256'] == frozen['corpora'][design]['sha256'], 'reference hash mismatch')
        target_profile = next(c['window_rates'] for c in corpora[design]['cases'] if c['name'] == target)
        verify_frozen_manifest(actual, frozen['templates'][f'{design}/{policy}'], seed, target_profile)
        rows.append({'design_key': design, **row})
        for name in FILES:
            path = relative / name
            hashes[str(path)] = hashlib.sha256((source / path).read_bytes()).hexdigest()
    return {'freeze_sha256': hashlib.sha256(raw).hexdigest(), 'spec': spec,
            'audited_cells': len(rows), 'audited_slots': len(rows) * spec['budget'],
            'inference': compare(rows, spec), 'rows': rows, 'artifact_sha256': hashes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--freeze', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    require(not args.archive.exists(), 'archive exists')
    result = build(args.source, args.freeze)
    args.archive.mkdir(parents=True)
    for name in result['artifact_sha256']:
        destination = args.archive / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.source / name, destination)
    shutil.copy2(args.freeze, args.archive / 'freeze.json')
    (args.archive / 'heldout.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Audited {result['audited_cells']} cells / {result['audited_slots']} slots")


if __name__ == '__main__':
    main()
