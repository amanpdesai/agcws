"""Replay archived v4 invalid patches against their original batch parents."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from agcws.policies.semantic_edits import apply_edits


def audit(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['policies'] != ['semantic-edits-v4'] or manifest['batch_size'] != 4:
        raise ValueError('replay is defined only for the frozen v4 batch-four controller')
    failures, missing, hashes = Counter(), 0, {}
    for path in sorted(directory.rglob('trials.jsonl')):
        data = path.read_bytes()
        hashes[str(path)] = hashlib.sha256(data).hexdigest()
        rows = [json.loads(line) for line in data.splitlines()]
        for start in range(0, len(rows), 4):
            parents = [r['workload'] for r in sorted(
                (r for r in rows[:start] if r['validity']['valid'] and r.get('loss') is not None),
                key=lambda r: r['loss'])[:4]]
            for row in rows[start:start + 4]:
                candidate = row['workload']
                if candidate == {}:
                    missing += 1
                elif '__invalid_semantic_patch__' in candidate:
                    try:
                        apply_edits(parents, candidate['__invalid_semantic_patch__'])
                    except (ValueError, TypeError, KeyError, IndexError) as exc:
                        failures[f'{type(exc).__name__}: {exc}'] += 1
                    else:
                        raise ValueError('archived failure did not reproduce')
    return {'archive': str(directory), 'invalid_patch_reasons': dict(failures),
            'missing_candidate_slots': missing, 'ledger_sha256': hashes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('archives', type=Path, nargs='+')
    args = parser.parse_args()
    result = {'scope': 'Post-hoc interface diagnosis; not a revised outcome or new held-out claim',
              'patch_implementation_sha256': hashlib.sha256(
                  Path('src/agcws/policies/semantic_edits.py').read_bytes()).hexdigest(),
              'panels': [audit(path) for path in args.archives]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
