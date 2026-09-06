"""Check that an unfinished fixed-horizon workload cannot receive a score."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from agcws import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.archive.exists():
        raise ValueError('output already exists')
    corpus = json.loads(Path('results/structural_temporal_dma_verification.json').read_text())
    case = next(r for r in corpus['cases'] if r['name'] == 'burst')
    args.out.mkdir(parents=True)
    source = args.out / 'workload.json'
    source.write_text(json.dumps(case['lowered_workload']['workload']) + '\n')
    with (args.out / 'driver.log').open('w') as log:
        result = subprocess.run(['bash', 'scripts/run_axi_dma_coupled.sh', str(source), str(args.out / 'simulation')],
                                env={**os.environ, 'AGCWS_DMA_TEST_MODULE': 'axi_dma_pipelined_tb',
                                     'AGCWS_DMA_OBSERVATION_CYCLES': '10', 'AGCWS_DMA_TRAILING_IDLE': '6000',
                                     'AGCWS_PYTHON': sys.executable, 'AGCWS_FST2VCD': str(config.FST2VCD)},
                                stdout=log, stderr=subprocess.STDOUT, check=False)
    log = (args.out / 'driver.log').read_text()
    reason = 'workload failed to complete within the declared observation horizon'
    if result.returncode == 0 or reason not in log:
        raise ValueError('expected explicit observation-horizon rejection did not occur')
    if (args.out / 'simulation/activity.json').exists():
        raise ValueError('failed simulation unexpectedly produced a scored activity artifact')
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with args.archive.open('x') as stream:
        stream.write(json.dumps({'passed': True, 'returncode': result.returncode,
                                 'rejection': reason, 'observation_cycles': 10,
                                 'activity_score_produced': False,
                                 'scope': 'negative fixed-horizon validity test, not a tool timeout'}, indent=2) + '\n')


if __name__ == '__main__':
    main()
