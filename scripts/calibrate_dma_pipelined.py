"""Collect twenty reference-checked workloads for the pipelined DMA envelope."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from agcws.adapters.axi_dma.pipelined import PipelinedDmaAdapter
from agcws.nodes.validation import validate_static
from agcws.policies.random_search import RandomSearch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    adapter = PipelinedDmaAdapter()
    rows = []
    for index, workload in enumerate(RandomSearch(0).propose(adapter, None, [], 20)):
        assert validate_static(adapter, workload).valid
        cell = args.out / f'trial-{index}'
        cell.mkdir(parents=True, exist_ok=True)
        source = cell / 'workload.json'
        source.write_text(json.dumps(workload) + '\n')
        if not (cell / 'activity.json').exists():
            with (cell / 'driver.log').open('w') as log:
                subprocess.run(['bash', 'scripts/run_axi_dma_coupled.sh', str(source), str(cell)],
                               env={**os.environ, 'AGCWS_DMA_TEST_MODULE': 'axi_dma_pipelined_tb',
                                    'AGCWS_PYTHON': sys.executable}, check=True, stdout=log,
                               stderr=subprocess.STDOUT)
        activity = json.loads((cell / 'activity.json').read_text())
        observed = json.loads((cell / 'sim_build/observed.json').read_text())
        assert observed['read_descriptors'] == observed['write_completions'] == len(workload['transfers'])
        useful = sum(t['length'] for t in workload['transfers'])
        assert useful >= adapter.useful_work_floor
        rows.append({'seed': 0, 'index': index, 'workload': workload, 'valid': True,
                     'useful_work': useful, 'observed': observed,
                     'clock_edges': activity['clock_edges'],
                     'activity': activity['total_transitions'] / activity['clock_edges']})
        print(f"DMA calibration {index + 1}/20 activity={rows[-1]['activity']:.4f}", flush=True)
    corpus = '\n'.join(json.dumps(row, sort_keys=True) for row in rows) + '\n'
    values = [row['activity'] for row in rows]
    aes = json.loads(Path('results/aes_transactions_calibration/calibration.json').read_text())
    calibration = {'backend': 'pipelined', 'count': 20, 'valid_count': 20,
                   'power_metric': 'total_transitions_per_clock_edge',
                   'p_min': min(values), 'p_max': max(values),
                   'epsilon_scalar': aes['epsilon_scalar'],
                   'epsilon_source': 'AES transaction five-seed rule; no DMA retuning',
                   'useful_work_floor': adapter.useful_work_floor,
                   'corpus_sha256': hashlib.sha256(corpus.encode()).hexdigest()}
    args.archive.mkdir(parents=True, exist_ok=True)
    (args.archive / 'corpus.jsonl').write_text(corpus)
    (args.archive / 'calibration.json').write_text(json.dumps(calibration, indent=2) + '\n')


if __name__ == '__main__':
    main()
