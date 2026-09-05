"""Equal-work, equal-idle temporal capability check on the transaction backend."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.nodes.validation import validate_static


def schedules():
    def crypto(n):
        return {'op': 'encrypt', 'blocks': n}

    def idle(n):
        return {'op': 'idle', 'cycles': n}

    return {
        'uniformly_paced': [op for _ in range(8) for op in (crypto(8), idle(750))],
        'burst_then_idle': [crypto(64), idle(6000)],
        'low_high_low': [idle(3000), crypto(64), idle(3000)],
        'alternating': [op for _ in range(4) for op in (crypto(16), idle(1500))],
        'ramp': [op for blocks, gap in zip([2, 4, 6, 8, 10, 12, 10, 12],
                                         [1500, 1300, 1100, 900, 600, 400, 200, 0])
                 for op in (crypto(blocks), idle(gap))],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, operations in schedules().items():
        workload = {'data_pattern': 1, 'operations': [{'op': 'configure', 'key_len': 128}, *operations]}
        assert sum(op.get('blocks', 0) for op in operations) == 64
        assert sum(op.get('cycles', 0) for op in operations) == 6000
        assert validate_static(AESTransactionAdapter(), workload).valid
        source = args.out / f'{name}.json'
        source.write_text(json.dumps(workload) + '\n')
        previous = None
        for repeat in range(2):
            cell = args.out / f'{name}-{repeat}'
            subprocess.run([sys.executable, 'scripts/run_aes_transactions.py', str(source),
                            '--out', str(cell)], check=True, capture_output=True, text=True)
            assert 'AES_CORE_WORKLOAD_DONE blocks=64' in (cell / 'run.log').read_text()
            activity = json.loads((cell / 'activity.json').read_text())
            toggles = activity['per_cycle_toggles']
            bins = [toggles[i * len(toggles) // 8:(i + 1) * len(toggles) // 8] for i in range(8)]
            rates = [sum(values) / len(values) for values in bins]
            measured = {'clock_edges': activity['clock_edges'], 'samples': len(toggles),
                        'mean_transitions_per_edge': activity['total_transitions'] / activity['clock_edges'],
                        'eight_bin_transitions_per_sample': rates}
            if previous is not None:
                assert measured == previous
            previous = measured
        rows.append({'name': name, 'workload': workload, 'useful_work': 64,
                     'idle_cycles': 6000, 'deterministic_repeats': 2, **measured,
                     'provenance': json.loads((cell / 'provenance.json').read_text()),
                     'activity_sha256': hashlib.sha256((cell / 'activity.json').read_bytes()).hexdigest()})
        print(name, rates, flush=True)
    assert len({row['clock_edges'] for row in rows}) == 1
    assert all(row['samples'] == row['clock_edges'] for row in rows)
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    args.archive.write_text(json.dumps({'scope': 'Temporal capability check, not agent comparison or gate power',
                                      'window': 'Eight equal sample-count bins over full DUT-scoped RTL trace',
                                      'cases': rows}, indent=2) + '\n')


if __name__ == '__main__':
    main()
