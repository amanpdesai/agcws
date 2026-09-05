"""Verify concurrency controls using DUT handshakes and reference memory."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    settings = [(depth, 0, 6) for depth in [1, 2, 4, 8]] + [(8, 0, 0), (8, 6, 0), (8, 0, 6)]
    for index, (depth, read_pause, write_pause) in enumerate(settings):
        workload = {'transfers': [{'src': i * 4096, 'dst': (i + 8) * 4096,
                                  'length': 512, 'outstanding': depth} for i in range(8)],
                    'backpressure': {'period': 8, 'read_pause': read_pause, 'write_pause': write_pause}}
        source = args.out / f'case-{index}.json'
        source.write_text(json.dumps(workload) + '\n')
        cell = args.out / f'case-{index}'
        with (args.out / f'case-{index}.log').open('w') as log:
            subprocess.run(['bash', 'scripts/run_axi_dma_coupled.sh', str(source), str(cell)],
                           env={**os.environ, 'AGCWS_DMA_TEST_MODULE': 'axi_dma_pipelined_tb',
                                'AGCWS_PYTHON': sys.executable}, check=True, stdout=log,
                           stderr=subprocess.STDOUT)
        observed = json.loads((cell / 'sim_build/observed.json').read_text())
        assert observed['read_descriptors'] == observed['write_completions'] == 8
        assert 1 <= observed['max_inflight'] <= depth
        if depth > 1:
            assert observed['max_inflight'] > 1
        activity = json.loads((cell / 'activity.json').read_text())
        rows.append({'depth': depth, 'backpressure': workload['backpressure'], **observed, 'clock_edges': activity['clock_edges'],
                     'activity': activity['total_transitions'] / activity['clock_edges']})
        print(rows[-1], flush=True)
    assert rows[3] == rows[6]
    assert rows[3]['clock_edges'] != rows[4]['clock_edges']
    assert rows[5]['clock_edges'] != rows[4]['clock_edges']
    (args.out / 'verification.json').write_text(json.dumps({'passed': True, 'cases': rows}, indent=2) + '\n')


if __name__ == '__main__':
    main()
