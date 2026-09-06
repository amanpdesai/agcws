"""Serial, foreground structural panel with per-cell logs and explicit failures."""
import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = args.spec.read_bytes()
    spec = json.loads(raw)
    if spec['phase'] != 'development' or spec['batch_size'] != 4:
        raise ValueError('this runner is for batch-four development only')
    axes = [spec[key] for key in ('designs', 'targets', 'seeds', 'policies')]
    if any(not axis or len(set(axis)) != len(axis) for axis in axes):
        raise ValueError('empty or duplicated panel axis')
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'panel_manifest.json').write_text(json.dumps({
        'spec': spec, 'spec_sha256': hashlib.sha256(raw).hexdigest(),
    }, indent=2) + '\n')
    failures = 0
    with (args.out / 'progress.jsonl').open('x') as progress:
        for design, target, seed, policy in itertools.product(*axes):
            cell = args.out / design / target / f'seed-{seed}' / policy
            cell.parent.mkdir(parents=True, exist_ok=True)
            command = [sys.executable, 'scripts/run_structural_search.py',
                       '--design', design, '--target', target, '--seed', str(seed),
                       '--policy', policy, '--budget', str(spec['budget']), '--out', str(cell)]
            print(f'START {design} {target} seed={seed} {policy}', flush=True)
            with cell.with_suffix('.log').open('x') as log:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
            status = {'design': design, 'target': target, 'seed': seed,
                      'policy': policy, 'returncode': result.returncode,
                      'summary_exists': (cell / 'summary.json').is_file()}
            if result.returncode or not status['summary_exists']:
                failures += 1
            progress.write(json.dumps(status) + '\n')
            progress.flush()
            print(json.dumps(status), flush=True)
    print(f'PANEL_FINISHED failures={failures}; audit required before interpretation', flush=True)
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
