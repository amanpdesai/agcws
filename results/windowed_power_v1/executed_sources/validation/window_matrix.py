"""Run only the declared finalist/reference native-window measurements."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from validation.window_power import evaluate

SYNTHESIS = {'aes': Path('out/aes-unmasked-matched-synthesis-v2'),
             'dma': Path('out/axi-dma-synthesis-gls3')}


def jobs(root, kind):
    if kind == 'finalists':
        cases = json.loads(Path('results/structural_temporal_finalists_v1.json').read_text())['cases']
        for case in cases:
            key, design = case['replay_id'], case['design']
            rtl = Path('out/structural-temporal-heldout-v1') / case['run'] / 'evaluations' / f'trial-{case["evaluation_index"]:05d}'
            gls = Path('out/structural-temporal-finalists-v1/replays') / key / 'gls'
            yield key, design, rtl, gls, root/'measurements'/'finalists'/key
    else:
        for design in ('aes', 'dma'):
            for target in ('random_300', 'random_301'):
                source = root/'references'/design/target
                completed = json.loads((source/'completed.json').read_text())
                yield f'{design}/{target}', design, Path(completed['rtl']), source/'gls', root/'measurements'/'references'/design/target


def run(job):
    key, design, rtl, gls, out = job
    n = json.loads((rtl/'activity.json').read_text())['clock_edges']
    evaluate(gls/'activity.vcd', rtl/'activity.vcd', SYNTHESIS[design],
             'clk_i' if design == 'aes' else 'clk',
             'aes_core_smoke/dut' if design == 'aes' else 'axi_dma', n, out)
    return key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('out/window-power-v1'))
    parser.add_argument('--kind', choices=['finalists', 'references'], required=True)
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('use 1..4 bounded workers')
    pending = list(jobs(args.root, args.kind))
    if any(job[-1].exists() for job in pending):
        raise ValueError('output already exists; preserve it and choose a fresh measurement root')
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run, job): job[0] for job in pending}
        for future in as_completed(futures):
            try:
                print('WINDOW_POWER_VERIFIED', future.result(), flush=True)
            except Exception as exc:
                failures.append({'case': futures[future], 'error': repr(exc)})
                print('WINDOW_POWER_FAILED', failures[-1], flush=True)
    if failures:
        raise RuntimeError(f'{len(failures)} cases failed; raw diagnostics retained')


if __name__ == '__main__':
    main()
