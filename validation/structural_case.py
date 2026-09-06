"""Replay one predeclared seed-400 finalist while the full panel continues."""
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from agcws import config
from agcws.adapters.aes.temporal import AESTemporalAdapter
from agcws.adapters.axi_dma.temporal import DmaTemporalAdapter
from agcws.experiments.freeze import verify_frozen_manifest
from agcws.workloads.schedule import ScheduleContract
from analysis.archive_matched_aes_gls import archive as archive_aes
from analysis.archive_matched_dma_gls import archive as archive_dma
from analysis.audit_structural_panel import audit_cell
from analysis.select_structural_finalists import choose
from validation.aes_gls import sha


def run_case(args):
    frozen_data = args.freeze.read_bytes()
    frozen = json.loads(frozen_data)
    spec = frozen['spec']
    if (args.design not in spec['designs'] or args.target not in spec['targets']
            or args.policy not in spec['policies'] or 400 not in spec['seeds']):
        raise ValueError('case is not a declared seed-400 finalist')
    relative = Path(args.design) / args.target / 'seed-400' / args.policy
    directory = args.runs / relative
    _, manifest, reference = audit_cell(directory, args.design, args.target, 400, args.policy, 32)
    corpus_bytes = Path(frozen['corpora'][args.design]['path']).read_bytes()
    if hashlib.sha256(corpus_bytes).hexdigest() != frozen['corpora'][args.design]['sha256']:
        raise ValueError('frozen corpus changed')
    target = next(c for c in json.loads(corpus_bytes)['cases'] if c['name'] == args.target)
    verify_frozen_manifest(manifest, frozen['templates'][f'{args.design}/{args.policy}'], 400, target['window_rates'])
    for name, expected in manifest['source_hashes'].items():
        if sha(name) != expected:
            raise ValueError(f'frozen runtime source changed: {name}')
    if reference.get('freeze_sha256') != hashlib.sha256(frozen_data).hexdigest():
        raise ValueError('cell freeze identity mismatch')
    trials_bytes = (directory / 'trials.jsonl').read_bytes()
    trials = [json.loads(line) for line in trials_bytes.splitlines()]
    selected = choose(trials)
    if selected is None:
        raise ValueError('no valid finalist; retain this case as missing, do not substitute a seed')
    index, evaluation, trial = selected
    replay = {'design': args.design, 'workload': trial['workload'],
              'observation_cycles': trial['goal']['observation_cycles'],
              'contract': manifest['workload_contract'], 'source_digest': manifest['source_digest']}
    ident = hashlib.sha256(json.dumps(replay, sort_keys=True).encode()).hexdigest()
    rtl = directory / 'evaluations' / f'trial-{evaluation:05d}'
    adapter = {'aes': AESTemporalAdapter, 'dma': DmaTemporalAdapter}[args.design](
        ScheduleContract(**manifest['workload_contract']))
    lowered = adapter.elaborate(trial['workload'])
    actual_workload = json.loads((rtl / 'workload.json').read_text())
    if actual_workload != (lowered if args.design == 'aes' else lowered['workload']):
        raise ValueError('raw workload does not match selected schedule')
    if args.design == 'dma':
        observed = json.loads((rtl / 'sim_build/observed.json').read_text())
        if observed['trailing_idle_cycles'] != lowered['trailing_idle_cycles']:
            raise ValueError('raw trailing idle differs from selected schedule')
    measured = json.loads((rtl / 'activity.json').read_text())
    samples, edges = measured['per_cycle_toggles'], measured['clock_edges']
    rates = [sum(samples[i*edges//8:(i+1)*edges//8]) / ((i+1)*edges//8-i*edges//8) for i in range(8)]
    if edges != replay['observation_cycles'] or rates != trial['profile']['windowed']:
        raise ValueError('raw RTL evaluation does not match selected trial')
    synthesis = json.loads((args.synthesis / 'manifest.json').read_text())
    if sha(config.LIBERTY) != synthesis['liberty_sha256']:
        raise ValueError('configured Liberty differs from synthesis')
    inputs = {'synthesis_manifest': sha(args.synthesis / 'manifest.json'),
              'netlist': sha(args.synthesis / 'mapped.v'), 'liberty': sha(config.LIBERTY),
              'cell_models': sha(os.environ['AGCWS_SKY130_CELL_MODELS']),
              'primitive_models': sha(os.environ['AGCWS_SKY130_PRIMITIVES']),
              'rtl_workload': sha(rtl / 'workload.json'),
              'validation_driver': sha(Path(__file__)),
              'design_driver': sha(Path(f'validation/{args.design}_gls.py'))}
    root = args.out / 'replays' / ident
    completion = root / 'completed.json'
    if completion.exists():
        record = json.loads(completion.read_text())
        if record['inputs'] != inputs or record['replay'] != replay:
            raise ValueError('cached validation inputs changed')
        if record['comparison_sha256'] != sha(root / 'archive/comparison.json'):
            raise ValueError('cached comparison changed')
        cached = True
    else:
        root.mkdir(parents=True, exist_ok=False)
        (root / 'replay.json').write_text(json.dumps(replay, indent=2) + '\n')
        gls = root / 'gls'
        start = time.monotonic()
        command = [os.sys.executable, '-m', f'validation.{args.design}_gls']
        if args.design == 'aes':
            command += ['replay', '--synthesis', str(args.synthesis), '--workload', str(rtl / 'workload.json'),
                        '--clock-edges', str(edges), '--out', str(gls)]
        else:
            command += ['--synthesis', str(args.synthesis), '--rtl', str(rtl), '--out', str(gls)]
        with (root / 'validation.log').open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            power_script = 'scripts/run_opensta_aes.sh' if args.design == 'aes' else 'scripts/run_opensta_axi_dma.sh'
            subprocess.run(['bash', power_script, str(args.synthesis), str(gls / 'activity.vcd'), str(gls / 'power')],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        (archive_aes if args.design == 'aes' else archive_dma)(rtl, gls, args.synthesis, root / 'archive')
        record = {'replay': replay, 'inputs': inputs, 'wall_clock_s': time.monotonic()-start,
                  'comparison_sha256': sha(root / 'archive/comparison.json')}
        completion.write_text(json.dumps(record, indent=2) + '\n')
        cached = False
    case = {'run': str(relative), 'replay_id': ident, 'proposal_index': index + 1,
            'evaluation_index': evaluation, 'trials_sha256': hashlib.sha256(trials_bytes).hexdigest(),
            'freeze_sha256': hashlib.sha256(frozen_data).hexdigest(), 'cache_reused': cached,
            'scope': 'Individual declared finalist; full-panel reconciliation still required.'}
    cases = args.out / 'cases'
    cases.mkdir(parents=True, exist_ok=True)
    with (cases / f'{args.design}-{args.target}-{args.policy}.json').open('x') as stream:
        stream.write(json.dumps(case, indent=2) + '\n')
    print(f'FINALIST_VALIDATED {relative} replay={ident} cached={cached}', flush=True)


def main():
    config._load_dotenv()
    parser = argparse.ArgumentParser()
    for name in ('runs', 'freeze', 'synthesis', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--design', choices=['aes', 'dma'], required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--policy', required=True)
    run_case(parser.parse_args())


if __name__ == '__main__':
    main()
