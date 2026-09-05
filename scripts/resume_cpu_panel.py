"""Resume a fixed CPU-only panel with managed workers and per-cell auditing."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys

from agcws.analysis.ledger_audit import audit_scalar_cell


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    manifest = json.loads((args.out / 'manifest.json').read_text())
    if not 1 <= args.workers <= 8:
        parser.error('workers must be 1..8')
    if set(manifest['policies']) - {'random', 'mutation', 'evolutionary', 'scalar-edit-evolution', 'coverage-guided-line'}:
        parser.error('only CPU policies may use this runner; Vertex remains serial')
    if (manifest['design'], manifest['backend']) not in [('dma', 'pipelined'), ('aes', 'transactions')]:
        parser.error('requires pipelined DMA or transaction AES')
    if manifest['design'] == 'dma' and 'coverage-guided-line' in manifest['policies']:
        parser.error('DMA does not expose instrumented coverage')
    execution = {'workers': args.workers, 'source_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'scope': 'Scheduling-only resume; original conditions retained. Wall-clock results mix serial and parallel execution.'}
    args.archive.mkdir(parents=True, exist_ok=True)
    (args.archive / 'execution.json').write_text(json.dumps(execution, indent=2) + '\n')
    (args.archive / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

    def run(policy, target, seed):
        relative = Path(policy) / f'target-{target:.2f}' / f'seed-{seed}'
        cell = args.out / relative
        cell.mkdir(parents=True, exist_ok=True)
        resumed = (cell / 'summary.json').exists()
        if not resumed:
            calibration = manifest['calibration']
            command = ([sys.executable, 'scripts/run_axi_dma_search.py', '--backend', 'pipelined']
                       if manifest['design'] == 'dma' else
                       [sys.executable, 'scripts/run_aes_search.py', 'out/aes-core-synthesis-final2',
                        '--backend', 'transactions'])
            command += ['--policy', policy, '--target', str(target), '--seed', str(seed),
                       '--budget', str(manifest['budget']), '--batch-size', str(manifest['batch_size']),
                       '--epsilon', str(manifest['epsilon']), '--p-min', str(calibration['p_min']),
                       '--p-max', str(calibration['p_max']), '--out', str(cell)]
            print(f'running {policy} q={target} seed={seed}', flush=True)
            with (cell / 'driver.log').open('w') as log:
                subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
        summary = json.loads((cell / 'summary.json').read_text())
        if (summary['policy'], summary['target'], summary['seed'], summary['budget'], summary['epsilon']) != (
                policy, target, seed, manifest['budget'], manifest['epsilon']):
            raise ValueError(f'cell configuration mismatch: {cell}')
        trials = [json.loads(line) for line in (cell / 'trials.jsonl').read_text().splitlines()]
        audit_scalar_cell(summary, trials, manifest['calibration'])
        for trial in trials:
            if trial.get('profile'):
                trial['profile'] = {k: v for k, v in trial['profile'].items()
                                    if k not in ('per_cycle_toggles', 'windowed')}
        dest = args.archive / relative
        dest.mkdir(parents=True, exist_ok=True)
        (dest / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        (dest / 'trials.jsonl').write_text('\n'.join(json.dumps(t) for t in trials) + '\n')
        if (cell / 'run_manifest.json').exists():
            (dest / 'run_manifest.json').write_bytes((cell / 'run_manifest.json').read_bytes())
        elif manifest['stage'] == 'evaluation':
            raise ValueError('held-out cell lacks source provenance')
        print(f"audited {policy} q={target} seed={seed} resumed={resumed} AUC={summary['auc_best_so_far']:.4f}", flush=True)
        return summary

    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run, p, t, s) for t in manifest['targets']
                   for s in manifest['seeds'] for p in manifest['policies']]
        for future in as_completed(futures):
            rows.append(future.result())
            rows.sort(key=lambda r: (r['target'], r['seed'], r['policy']))
            (args.archive / 'summaries.json').write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    main()
