"""Publish compact, join-ready overlays; never modify frozen candidate records."""

import argparse
import json
import time
from pathlib import Path

from agcws.evaluation.power.candidate_revalidation import (
    VERSION,
    checked,
    native_setup,
    read,
    write,
)
from agcws.evidence.retention import file_digest
from agcws.reporting.power_reference import compare_measurements


def verify_revision(original, revised):
    if revised['activity'] != original['activity']:
        raise ValueError('revised activity differs from frozen case')
    for key, value in original.items():
        if key != 'power' and revised.get(key) != value:
            raise ValueError(f'revised measurement changes native field: {key}')
    for key, value in original['power'].items():
        if key not in ('switching_reconstruction', 'artifact_sha256') and revised['power'].get(key) != value:
            raise ValueError(f'revised measurement changes native power: {key}')
    if native_setup(original['power']) != native_setup(revised['power']):
        raise ValueError('cross-setup revision')
    if revised['power']['switching_reconstruction']['policy'] != 'slew-verified-v1':
        raise ValueError('revision lacks slew validation')


def publish(batch, destination):
    root = Path.cwd().resolve()
    batch, destination = batch.resolve(), destination.resolve()
    if not destination.is_relative_to(root / 'results/ibex/power'):
        raise ValueError('overlay must be under results/ibex/power')
    data = read(batch / 'inventory.json')
    input_hash = file_digest(batch / 'inventory.json')[0]
    destination.mkdir(parents=True, exist_ok=True)
    identity = destination / 'provenance.json'
    if identity.exists():
        if read(identity)['inventory_sha256'] != input_hash:
            raise ValueError('overlay belongs to another inventory')
    else:
        write(identity, {'version': VERSION, 'inventory_sha256': input_hash,
                         'archive': str(Path(data['archive']).relative_to(root)),
                         'archive_sha256': data['archive_sha256'],
                         'implementation_sha256': data['implementation_sha256'],
                         'references': data['references'], 'buckets': data['buckets']})
    portable_inputs = {str(identity.relative_to(root)): file_digest(identity)[0],
                       str(Path(data['archive']).relative_to(root)): data['archive_sha256']}
    for name, expected in data['implementation_sha256'].items():
        snapshot = batch / ('source-' + Path(name).name)
        checked(snapshot, expected)
        saved = destination / snapshot.name
        if saved.exists():
            checked(saved, expected)
        else:
            with saved.open('xb') as stream:
                stream.write(snapshot.read_bytes())
        portable_inputs[str(saved.relative_to(root))] = expected
    entries, failed, pending = {}, {}, []
    for case in data['cases']:
        if case['strict_pass']:
            continue
        case_id = case['case_id']
        work = batch / 'cases' / case_id
        status_file = work / 'status.json'
        status = read(status_file) if status_file.exists() else {'state': 'pending'}
        if status['state'] == 'failed':
            failed[case_id] = status
            continue
        if status['state'] != 'slew_verified':
            pending.append(case_id)
            continue
        source, revised_path = Path(case['source']), work / 'measurement.json'
        checked(source, case['source_sha256'])
        checked(revised_path, read(work / 'complete.json')['measurement_sha256'])
        original, revised = read(source), read(revised_path)
        verify_revision(original, revised)
        if revised['revalidation']['source_sha256'] != case['source_sha256']:
            raise ValueError('revision source hash differs')
        checked(case['reference']['path'], case['reference']['sha256'])
        compare_measurements(revised, read(case['reference']['path']))
        target = destination / f'{case_id}.json'
        raw = (json.dumps(revised, separators=(',', ':'), sort_keys=True)+'\n').encode()
        if target.exists():
            if target.read_bytes() != raw:
                raise ValueError('published overlay record changed')
        else:
            with target.open('xb') as stream:
                stream.write(raw)
        entries[case_id] = {'path': str(target.relative_to(root)),
                            'sha256': file_digest(target)[0],
                            'original_sha256': case['source_sha256']}
        portable_inputs[str(target.relative_to(root))] = entries[case_id]['sha256']
    index = {'version': VERSION, 'entries': entries, 'failed': failed, 'pending': pending,
             'expected_revisions': data['audit_required_count'], 'strict_unchanged': data['strict_pass_count'],
             'complete': not pending, 'all_passed': not pending and not failed,
             'scope': 'Only originally failed native-additivity nonflat Ibex candidates. Strict-pass cases unchanged; flat controls excluded.',
             'inventory_sha256': input_hash}
    index.update(inputs=portable_inputs, generator_sha256=file_digest(Path(__file__))[0],
                 portable_proof_dependencies='Proofs are embedded in each hashed revised measurement JSON. Raw reports and retained VCDs remain external, hash-addressed evidence.')
    write(destination / 'index.json', index)
    write(destination / 'mapping.json', entries)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    while True:
        index = publish(args.batch, args.out)
        print(json.dumps({'published': len(index['entries']), 'failed': len(index['failed']),
                          'pending': len(index['pending']), 'complete': index['complete']}), flush=True)
        if not args.watch or index['complete']:
            break
        time.sleep(30)


if __name__ == '__main__':
    main()
