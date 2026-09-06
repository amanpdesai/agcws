"""Shared fixed-work/window structural search over real AES and DMA DUTs."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from agcws import config
from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.adapters.axi_dma.temporal import DmaTemporalAdapter
from agcws.experiments.runner import run_search
from agcws.goals.schema import FixedTemporalGoal
from agcws.nodes.power import PowerProfile
from agcws.policies.structural import (
    StructuralEvolution,
    StructuralPopulationEvolution,
    StructuralRandom,
)
from agcws.policies.structural_agent import StructuralAgent, StructuralHybrid
from agcws.policies.structural_edit_agent import (
    StructuralEditAgent,
    StructuralEditHybrid,
    StructuralPopulationAgent,
    StructuralPopulationHybrid,
)
from agcws.workloads.schedule import ScheduleContract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--design', choices=['aes', 'dma'], default='aes')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--target', required=True)
    parser.add_argument('--policy', choices=['random', 'evolutionary', 'agent', 'hybrid', 'edit-agent', 'edit-hybrid',
                                            'population-evolution', 'population-agent', 'population-hybrid'], required=True)
    parser.add_argument('--prompt', type=Path)
    parser.add_argument('--seed', type=int, default=310)
    parser.add_argument('--budget', type=int, default=16)
    parser.add_argument('--scale', type=float)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.targets = args.targets or Path(f'results/structural_temporal_{args.design}_verification.json')
    args.scale = args.scale if args.scale is not None else {'aes': 200.0, 'dma': 40.0}[args.design]
    target_bytes = args.targets.read_bytes()
    corpus = json.loads(target_bytes)
    target = next(row for row in corpus['cases'] if row['name'] == args.target)
    contract = ScheduleContract(**corpus['contract'])
    adapter = {'aes': AESTemporalAdapter, 'dma': DmaTemporalAdapter}[args.design](contract)
    goal = FixedTemporalGoal(windows=8, profile=target['window_rates'], scale=args.scale,
                             observation_cycles=target['clock_edges'], tolerance=0.10)
    if args.out.exists():
        raise ValueError('output directory exists; refusing to overwrite or silently resume')
    args.out.mkdir(parents=True)
    (args.out / 'target_manifest.json').write_text(json.dumps({
        'phase': 'development-pilot', 'source': str(args.targets),
        'source_sha256': hashlib.sha256(target_bytes).hexdigest(),
        'reference_name': args.target, 'goal': vars(goal),
        'design': args.design,
        'scope': 'Fixed-work temporal development; no superiority or gate-power claim',
    }, indent=2) + '\n')
    index = 0

    def evaluate(schedule):
        nonlocal index
        directory = args.out / 'evaluations' / f'trial-{index:05d}'
        index += 1
        directory.mkdir(parents=True)
        source = directory / 'workload.json'
        lowered = adapter.elaborate(schedule)
        source.write_text(json.dumps(lowered if args.design == 'aes' else lowered['workload'], sort_keys=True) + '\n')
        command = [sys.executable, 'scripts/run_aes_transactions.py', str(source), '--out', str(directory)]
        environment = dict(os.environ)
        if args.design == 'dma':
            command = ['bash', 'scripts/run_axi_dma_coupled.sh', str(source), str(directory)]
            environment.update(AGCWS_DMA_TEST_MODULE='axi_dma_pipelined_tb',
                               AGCWS_DMA_OBSERVATION_CYCLES=str(goal.observation_cycles),
                               AGCWS_DMA_TRAILING_IDLE=str(lowered['trailing_idle_cycles']),
                               AGCWS_PYTHON=sys.executable, AGCWS_FST2VCD=str(config.FST2VCD))
        with (directory / 'driver.log').open('w') as driver_log:
            completed = subprocess.run(command, env=environment, check=False,
                                       stdout=driver_log, stderr=subprocess.STDOUT)
        if completed.returncode:
            raise RuntimeError(f'{args.design} failed; inspect {directory / "driver.log"}')
        if args.design == 'aes':
            match = re.search(r'AES_CORE_WORKLOAD_DONE blocks=(\d+)', (directory / 'run.log').read_text())
            useful_work = int(match[1]) if match else 0
            provenance = json.loads((directory / 'provenance.json').read_text())
        else:
            observed = json.loads((directory / 'sim_build/observed.json').read_text())
            if observed['read_descriptors'] != contract.work_units or observed['write_completions'] != contract.work_units:
                raise ValueError('DMA transfer completion count mismatch')
            useful_work = observed['useful_work_bytes']
            provenance = json.loads((directory / 'manifest.json').read_text())
            provenance['observed'] = observed
        if useful_work != adapter.useful_work_floor:
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
        provenance.update(clock_edges=edges, metric='DUT transitions per clock edge',
                          window='full trace including reset; equal-clock bins',
                          activity_sha256=hashlib.sha256(activity_path.read_bytes()).hexdigest())
        return PowerProfile(mean_power=activity['total_transitions'] / edges,
                            peak_power=max(rates), windowed=rates, useful_work=useful_work,
                            valid=True, fidelity='activity', provenance=provenance)

    if args.policy in ('agent', 'hybrid', 'edit-agent', 'edit-hybrid', 'population-agent', 'population-hybrid'):
        config._load_dotenv()
        required = ['AGCWS_GCP_PROJECT', 'AGCWS_GEMINI_MODEL',
                    'AGCWS_GEMINI_INPUT_USD_PER_MILLION', 'AGCWS_GEMINI_OUTPUT_USD_PER_MILLION']
        if any(not os.getenv(key) for key in required):
            raise ValueError('Vertex project/model and explicit token pricing are required')
        if any(float(os.environ[key]) <= 0 for key in required[2:]):
            raise ValueError('positive model token rates are required')
        cls = {'agent': StructuralAgent, 'hybrid': StructuralHybrid,
               'edit-agent': StructuralEditAgent, 'edit-hybrid': StructuralEditHybrid,
               'population-agent': StructuralPopulationAgent,
               'population-hybrid': StructuralPopulationHybrid}[args.policy]
        prompt = args.prompt or Path('prompts/structural_temporal_edits_v2.txt' if args.policy.startswith(('edit-', 'population-'))
                                     else 'prompts/structural_temporal_v1.txt')
        policy = cls.from_vertex(prompt.read_text(), model=os.environ['AGCWS_GEMINI_MODEL'],
                                 project=os.environ['AGCWS_GCP_PROJECT'],
                                 location=os.getenv('AGCWS_GCP_LOCATION', 'global')).initialize(args.seed)
    else:
        policy = {'random': StructuralRandom, 'evolutionary': StructuralEvolution,
                  'population-evolution': StructuralPopulationEvolution}[args.policy](args.seed)
    run_search(adapter, policy, goal, evaluate, budget=args.budget, batch_size=4,
               seed=args.seed, output_dir=args.out)
    print((args.out / 'summary.json').read_text())


if __name__ == '__main__':
    main()
