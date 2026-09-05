"""Calibrate the transaction oracle and apply the five-seed tolerance rule."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from agcws.adapters.aes import AESAdapter
from agcws.policies.random_search import RandomSearch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    adapter = AESAdapter()
    rows = []
    for seed in range(5):
        for index, workload in enumerate(RandomSearch(seed).propose(adapter, None, [], 20)):
            cell = args.out / f'seed-{seed}' / f'trial-{index}'
            cell.mkdir(parents=True, exist_ok=True)
            source = cell / 'workload.json'
            source.write_text(json.dumps(workload, sort_keys=True) + '\n')
            if not (cell / 'activity.json').exists():
                with (cell / 'driver.log').open('w') as log:
                    subprocess.run([sys.executable, 'scripts/run_aes_transactions.py', str(source),
                                    '--out', str(cell)], check=True, stdout=log, stderr=subprocess.STDOUT)
            activity = json.loads((cell / 'activity.json').read_text())
            useful = sum(op.get('blocks', 0) for op in workload['operations'])
            if useful < adapter.useful_work_floor:
                raise ValueError('calibration workload below useful-work floor')
            if f'AES_CORE_WORKLOAD_DONE blocks={useful}' not in (cell / 'run.log').read_text():
                raise ValueError('completion marker mismatch')
            rows.append({'seed': seed, 'index': index, 'workload': workload,
                         'useful_work': useful, 'valid': True,
                         'activity': activity['total_transitions'] / activity['clock_edges'],
                         'clock_edges': activity['clock_edges'],
                         'provenance': json.loads((cell / 'provenance.json').read_text())})
        print(f'calibration seed {seed} complete', flush=True)
    envelope = [r['activity'] for r in rows if r['seed'] == 0]
    lo, hi = min(envelope), max(envelope)

    def fractions(epsilon):
        return [sum(any(abs((r['activity'] - lo) / (hi - lo) - target) <= epsilon
                        for r in rows if r['seed'] == seed)
                    for target in [0.1, 0.25, 0.5, 0.75, 0.9]) / 5 for seed in range(5)]

    base = fractions(0.05)
    r = median(base)
    epsilon = 0.02 if r > 0.6 else (0.10 if r < 0.1 else 0.05)
    final = fractions(epsilon)
    calibration = {'backend': 'transactions', 'power_metric': 'total_transitions_per_clock_edge',
                   'scope': 'aes_core_smoke.dut', 'count': 20, 'valid_count': 20,
                   'p_min': lo, 'p_max': hi, 'useful_work_floor': adapter.useful_work_floor,
                   'useful_work_min': min(r['useful_work'] for r in rows[:20]),
                   'epsilon_scalar': epsilon, 'random_solved_fraction_base': r,
                   'base_seed_fractions': base, 'final_seed_fractions': final,
                   'random_solved_fraction': median(final),
                   'status': 'five_seed_calibration_before_transaction_comparisons',
                   'g3_trivial': epsilon == 0.02 and median(final) > 0.6}
    args.archive.mkdir(parents=True, exist_ok=True)
    corpus = '\n'.join(json.dumps(row, sort_keys=True) for row in rows) + '\n'
    calibration['corpus_sha256'] = hashlib.sha256(corpus.encode()).hexdigest()
    (args.archive / 'corpus.jsonl').write_text(corpus)
    (args.archive / 'calibration.json').write_text(json.dumps(calibration, indent=2) + '\n')
    print(json.dumps(calibration, indent=2))


if __name__ == '__main__':
    main()
