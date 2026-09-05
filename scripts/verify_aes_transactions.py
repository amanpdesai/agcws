"""Exercise every advertised AES mode and exact workload idle timing."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []

    def run(name, workload):
        path = args.out / (name + '.json')
        path.write_text(json.dumps(workload) + '\n')
        directory = args.out / name
        subprocess.run([sys.executable, 'scripts/run_aes_transactions.py', str(path),
                        '--out', str(directory)], check=True, capture_output=True, text=True)
        activity = json.loads((directory / 'activity.json').read_text())
        coverage = json.loads((directory / 'coverage.json').read_text())
        log = (directory / 'run.log').read_text()
        assert 'AES_CORE_WORKLOAD_DONE blocks=38' in log
        row = {'name': name, 'clock_edges': activity['clock_edges'],
               'activity': activity['total_transitions'] / activity['clock_edges'],
               'coverage_hit': sum(n > 0 for n in coverage.values()), 'coverage_total': len(coverage)}
        rows.append(row)
        return row

    for bits in [128, 192, 256]:
        for direction in ['encrypt', 'decrypt']:
            for pattern in range(4):
                run(f'{bits}-{direction}-{pattern}', {'data_pattern': pattern, 'operations': [
                    {'op': 'configure', 'key_len': bits}, {'op': direction, 'blocks': 38}]})
    baseline = rows[0]
    workload = {'data_pattern': 0, 'operations': [{'op': 'configure', 'key_len': 128},
                {'op': 'idle', 'cycles': 20}, {'op': 'encrypt', 'blocks': 38},
                {'op': 'idle', 'cycles': 30}]}
    idle = run('leading-and-trailing-idle', workload)
    assert idle['clock_edges'] - baseline['clock_edges'] == 50
    for repeat in range(2):
        repeated = run(f'idle-repeat-{repeat}', workload)
        assert repeated['clock_edges'] == idle['clock_edges']
        assert repeated['activity'] == idle['activity']
    mixed = {'data_pattern': 1, 'operations': []}
    for bits, count in [(128, 6), (192, 6), (256, 7)]:
        mixed['operations'] += [{'op': 'configure', 'key_len': bits},
                                {'op': 'encrypt', 'blocks': count},
                                {'op': 'decrypt', 'blocks': count}]
    run('mixed-directions-and-keys', mixed)
    (args.out / 'verification.json').write_text(json.dumps({'passed': True, 'cases': rows}, indent=2) + '\n')
    print(json.dumps({'passed': True, 'cases': len(rows)}))


if __name__ == '__main__':
    main()
