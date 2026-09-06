"""Verify repeat lowering and fixed-work/window AES schedules on real RTL."""
import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from agcws.adapters.aes.temporal import lower_schedule
from agcws.workloads.schedule import ScheduleContract, random_schedule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    if args.archive.exists():
        raise ValueError('archive already exists')
    contract = ScheduleContract(64, 6000)
    body = [{'op': 'work', 'units': 8}, {'op': 'wait', 'cycles': 750}]
    schedules = {'repeat': {'sequence': [{'op': 'repeat', 'count': 8, 'body': body}]},
                 'expanded': {'sequence': body * 8},
                 'random_300': random_schedule(random.Random(300), contract),
                 'random_301': random_schedule(random.Random(301), contract)}
    rows = []
    for name, schedule in schedules.items():
        directory = args.out / name
        directory.mkdir(parents=True, exist_ok=False)
        workload = lower_schedule(schedule, contract)
        path = directory / 'workload.json'
        path.write_text(json.dumps(workload, sort_keys=True) + '\n')
        subprocess.run([sys.executable, 'scripts/run_aes_transactions.py', str(path),
                        '--out', str(directory)], check=True, capture_output=True, text=True)
        log = (directory / 'run.log').read_text()
        match = re.search(r'AES_CORE_WORKLOAD_DONE blocks=(\d+)', log)
        if not match or int(match[1]) != contract.work_units:
            raise ValueError('functional/useful-work verification failed')
        activity = json.loads((directory / 'activity.json').read_text())
        samples = activity['per_cycle_toggles']
        edges = activity['clock_edges']
        if len(samples) != edges or edges != 6774:
            raise ValueError('measurement duration is not the reference fixed window')
        bins = [samples[i * edges // 8:(i + 1) * edges // 8] for i in range(8)]
        rates = [sum(values) / len(values) for values in bins]
        rows.append({'name': name, 'schedule': schedule, 'lowered_workload': workload,
                     'clock_edges': edges, 'useful_work': int(match[1]), 'window_rates': rates,
                     'activity_sha256': hashlib.sha256((directory / 'activity.json').read_bytes()).hexdigest(),
                     'provenance': json.loads((directory / 'provenance.json').read_text())})
        print(name, edges, rates, flush=True)
    if rows[0]['activity_sha256'] != rows[1]['activity_sha256']:
        raise ValueError('compact repeat and explicit expansion differ in measured activity')
    result = {'scope': 'Representation and fixed-window verification, not comparative search',
              'contract': asdict(contract), 'window': 'full trace including reset; eight equal-clock bins',
              'cases': rows}
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with args.archive.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
