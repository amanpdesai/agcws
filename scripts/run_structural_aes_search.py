"""Small fixed-work/window structural search on the real AES transaction DUT."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import FixedTemporalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.structural import StructuralEvolution, StructuralRandom
from agcws.workloads.schedule import ScheduleContract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', type=Path, default=Path('results/structural_temporal_aes_verification.json'))
    parser.add_argument('--target', required=True)
    parser.add_argument('--policy', choices=['random', 'evolutionary'], required=True)
    parser.add_argument('--seed', type=int, default=310)
    parser.add_argument('--budget', type=int, default=16)
    parser.add_argument('--scale', type=float, default=200.0)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    target_bytes = args.targets.read_bytes()
    corpus = json.loads(target_bytes)
    target = next(row for row in corpus['cases'] if row['name'] == args.target)
    contract = ScheduleContract(**corpus['contract'])
    adapter = AESTemporalAdapter(contract)
    goal = FixedTemporalGoal(windows=8, profile=target['window_rates'], scale=args.scale,
                             observation_cycles=target['clock_edges'], tolerance=0.10)
    if args.out.exists():
        raise ValueError('output directory exists; refusing to overwrite or silently resume')
    args.out.mkdir(parents=True)
    (args.out / 'target_manifest.json').write_text(json.dumps({
        'phase': 'development-pilot', 'source': str(args.targets),
        'source_sha256': hashlib.sha256(target_bytes).hexdigest(),
        'reference_name': args.target, 'goal': vars(goal),
        'scope': 'AES-128 fixed-work temporal activity; no agent or gate-power claim',
    }, indent=2) + '\n')
    index = 0

    def evaluate(schedule):
        nonlocal index
        directory = args.out / 'evaluations' / f'trial-{index:05d}'
        index += 1
        directory.mkdir(parents=True)
        source = directory / 'workload.json'
        source.write_text(json.dumps(adapter.elaborate(schedule), sort_keys=True) + '\n')
        completed = subprocess.run([sys.executable, 'scripts/run_aes_transactions.py', str(source),
                                    '--out', str(directory)], check=False, capture_output=True, text=True)
        if completed.returncode:
            raise RuntimeError(f'AES failed: {completed.stderr[-2000:]}')
        match = re.search(r'AES_CORE_WORKLOAD_DONE blocks=(\d+)', (directory / 'run.log').read_text())
        if not match or int(match[1]) != contract.work_units:
            raise ValueError('functional/exact useful-work check failed')
        activity_path = directory / 'activity.json'
        activity = json.loads(activity_path.read_text())
        samples = activity['per_cycle_toggles']
        edges = activity['clock_edges']
        if len(samples) != edges or edges != goal.observation_cycles:
            raise ValueError('fixed measurement window mismatch')
        bins = [samples[i * edges // goal.windows:(i + 1) * edges // goal.windows]
                for i in range(goal.windows)]
        rates = [sum(values) / len(values) for values in bins]
        provenance = json.loads((directory / 'provenance.json').read_text())
        provenance.update(clock_edges=edges, metric='DUT transitions per clock edge',
                          window='full trace including reset; equal-clock bins',
                          activity_sha256=hashlib.sha256(activity_path.read_bytes()).hexdigest())
        return PowerProfile(mean_power=activity['total_transitions'] / edges,
                            peak_power=max(rates), windowed=rates, useful_work=int(match[1]),
                            valid=True, fidelity='activity', provenance=provenance)

    policy = (StructuralRandom if args.policy == 'random' else StructuralEvolution)(args.seed)
    run_search(adapter, policy, goal, evaluate, budget=args.budget, batch_size=4,
               seed=args.seed, output_dir=args.out)
    print((args.out / 'summary.json').read_text())


if __name__ == '__main__':
    main()
