"""Run versioned scalar development cells and archive verified compact evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--design', choices=['aes', 'dma'], default='aes')
    parser.add_argument('--seeds', nargs='+', type=int, default=[100, 101, 102])
    parser.add_argument('--policies', nargs='+', default=['random', 'evolutionary', 'semantic-edits-v4'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    if any(seed < 100 or seed >= 200 for seed in args.seeds):
        parser.error('development seeds must be 100..199; held-out seeds are reserved')
    calibration_path = Path('experiments/calibration/aes_activity_calibration.json'
                            if args.design == 'aes' else 'out/axi-calibration-feedback/calibration.json')
    calibration = json.loads(calibration_path.read_text())
    prompt = Path('prompts/semantic_edits_v3.txt')
    manifest = {'stage': 'development', 'design': args.design, 'seeds': args.seeds,
                'policies': args.policies, 'budget': 50, 'batch_size': 4,
                'epsilon': 0.02, 'targets': [0.1, 0.25, 0.5, 0.75, 0.9],
                'calibration': calibration, 'prompt_sha256': hashlib.sha256(prompt.read_bytes()).hexdigest(),
                'model': os.environ.get('AGCWS_GEMINI_MODEL'),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    args.out.mkdir(parents=True, exist_ok=True)
    args.archive.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / 'manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise ValueError('manifest mismatch; use a new output directory for changed configuration')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    archived = []
    for target in manifest['targets']:
        for seed in args.seeds:
            for policy in args.policies:
                cell = args.out / policy / f'target-{target:.2f}' / f'seed-{seed}'
                summary_path = cell / 'summary.json'
                cell.mkdir(parents=True, exist_ok=True)
                if not summary_path.exists():
                    command = [sys.executable, 'scripts/run_aes_search.py', 'out/aes-core-synthesis-final2']
                    if args.design == 'dma':
                        command = [sys.executable, 'scripts/run_axi_dma_search.py']
                    command += ['--policy', policy, '--target', str(target), '--seed', str(seed),
                                '--budget', '50', '--batch-size', '4', '--epsilon', '0.02',
                                '--p-min', str(calibration['p_min']), '--p-max', str(calibration['p_max']),
                                '--prompt', str(prompt), '--out', str(cell)]
                    print(f'running {args.design} {policy} q={target} seed={seed}', flush=True)
                    with (cell / 'driver.log').open('w') as log:
                        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
                    if completed.returncode:
                        raise RuntimeError(f'cell failed: {cell}; inspect driver.log')
                summary = json.loads(summary_path.read_text())
                if (summary['budget'], summary['target'], summary['seed'], summary['epsilon']) != (50, target, seed, 0.02):
                    raise ValueError(f'cell configuration mismatch: {cell}')
                compact = []
                with (cell / 'trials.jsonl').open() as source:
                    for line in source:
                        trial = json.loads(line)
                        if trial['goal'] != {'q': target, 'tolerance': 0.02}:
                            raise ValueError('trial goal mismatch')
                        profile = trial.get('profile')
                        if profile:
                            trial['profile'] = {k: v for k, v in profile.items()
                                                if k not in ('per_cycle_toggles', 'windowed')}
                        compact.append(trial)
                if len(compact) != 50:
                    raise ValueError('incomplete trial ledger')
                dest = args.archive / policy / f'target-{target:.2f}' / f'seed-{seed}'
                dest.mkdir(parents=True, exist_ok=True)
                (dest / 'trials.jsonl').write_text('\n'.join(json.dumps(t) for t in compact) + '\n')
                (dest / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
                archived.append(summary)
                (args.archive / 'summaries.json').write_text(json.dumps(archived, indent=2) + '\n')
                (args.archive / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
                print(f"AUC={summary['auc_best_so_far']:.4f} valid={summary['valid_trials']}/50", flush=True)


if __name__ == '__main__':
    main()
