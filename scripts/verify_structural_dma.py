"""Measure deterministic fixed-horizon schedules and DMA concurrency on real RTL."""
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from agcws import config
from agcws.adapters.axi_dma.temporal import lower_schedule
from agcws.workloads.schedule import ScheduleContract, random_schedule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--horizon', type=int, default=12000)
    args = parser.parse_args()
    if args.out.exists() or args.archive.exists():
        raise ValueError('output or archive exists')
    args.out.mkdir(parents=True)
    contract = ScheduleContract(64, 6000)
    work = {'op': 'work', 'units': 64}
    schedules = {
        'burst': {'sequence': [work, {'op': 'wait', 'cycles': 6000}]},
        'low_high_low': {'sequence': [{'op': 'wait', 'cycles': 3000}, work, {'op': 'wait', 'cycles': 3000}]},
        'uniform': {'sequence': [{'op': 'repeat', 'count': 8, 'body': [
            {'op': 'work', 'units': 8}, {'op': 'wait', 'cycles': 750}]}]},
        'serial': {'sequence': [{'op': 'repeat', 'count': 63, 'body': [
            {'op': 'work', 'units': 1}, {'op': 'wait', 'cycles': 93}]},
            {'op': 'work', 'units': 1}, {'op': 'wait', 'cycles': 141}]},
        'random_300': random_schedule(random.Random(300), contract),
        'random_301': random_schedule(random.Random(301), contract),
    }
    rows = []
    for name, schedule in schedules.items():
        lowered = lower_schedule(schedule, contract)
        source = args.out / f'{name}.json'
        source.write_text(json.dumps(lowered['workload'], sort_keys=True) + '\n')
        previous, artifacts = None, []
        for repeat in range(2):
            directory = args.out / f'{name}-{repeat}'
            with (args.out / f'{name}-{repeat}.log').open('w') as log:
                subprocess.run(['bash', 'scripts/run_axi_dma_coupled.sh', str(source), str(directory)],
                               env={**os.environ, 'AGCWS_DMA_TEST_MODULE': 'axi_dma_pipelined_tb',
                                    'AGCWS_DMA_OBSERVATION_CYCLES': str(args.horizon),
                                    'AGCWS_DMA_TRAILING_IDLE': str(lowered['trailing_idle_cycles']),
                                    'AGCWS_PYTHON': sys.executable, 'AGCWS_FST2VCD': str(config.FST2VCD)},
                               check=True, stdout=log, stderr=subprocess.STDOUT)
            activity_path = directory / 'activity.json'
            activity = json.loads(activity_path.read_text())
            observed = json.loads((directory / 'sim_build/observed.json').read_text())
            if (observed['read_descriptors'] != 64 or observed['write_completions'] != 64
                    or observed['useful_work_bytes'] != 4096):
                raise ValueError('DMA completion/useful-work verification failed')
            samples, edges = activity['per_cycle_toggles'], activity['clock_edges']
            if len(samples) != edges or edges != args.horizon:
                raise ValueError(f'waveform horizon mismatch: {edges} edges, expected {args.horizon}')
            bins = [samples[i * edges // 8:(i + 1) * edges // 8] for i in range(8)]
            canonical = {k: v for k, v in activity.items() if k != 'waveform_sha256'}
            measured = {'clock_edges': edges, 'window_rates': [sum(v) / len(v) for v in bins],
                        'measurement_sha256': hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest(),
                        'observed': observed}
            artifacts.append({'repeat': repeat, 'activity_sha256': hashlib.sha256(activity_path.read_bytes()).hexdigest(),
                              'waveform_sha256': activity['waveform_sha256']})
            if previous is not None and measured != previous:
                raise ValueError('identical DMA schedule produced nondeterministic activity or timing')
            previous = measured
        rows.append({'name': name, 'schedule': schedule, 'lowered_workload': lowered,
                     'deterministic_repeats': 2, 'repeat_artifacts': artifacts,
                     'provenance': json.loads((directory / 'manifest.json').read_text()), **measured})
        print(name, observed['max_inflight'], observed['completion_ns'], measured['window_rates'], flush=True)
    by_name = {r['name']: r for r in rows}
    if by_name['serial']['observed']['max_inflight'] != 1 or by_name['burst']['observed']['max_inflight'] <= 1:
        raise ValueError('work grouping did not change actual observed concurrency')
    result = {'scope': 'DMA temporal capability and fixed-window verification, not agent comparison',
              'contract': asdict(contract), 'work_quantum_bytes': 64,
              'observation_cycles': args.horizon, 'clock_period_ns': 10,
              'window': 'full trace including reset and fixed-horizon padding; eight equal-clock bins',
              'cases': rows}
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with args.archive.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
