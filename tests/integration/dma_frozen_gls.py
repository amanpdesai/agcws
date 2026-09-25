"""CPU-only frozen DMA -> reference-checked GLS -> eight-window OpenSTA receipt."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from agcws.core import config
from agcws.designs.aes.gls import sha
from agcws.evaluation.power.finalists import restore
from agcws.evaluation.power.frozen import replay, verify_sources
from agcws.evaluation.power.windows import evaluate
from agcws.studies.finalists import read, verify


def finish(out, plan, case, synthesis, runtime):
    """Check and record completed functional replays, then run native power."""
    verify(plan)
    manifest = read(Path(case['root']) / 'manifest.json')
    verify_sources(manifest, runtime)
    mapped = read(synthesis / 'manifest.json')
    for path, digest in mapped['sources'].items():
        if manifest['sources'].get(path) != digest:
            raise ValueError('mapped RTL differs from the frozen measurement RTL')
    result = read(out / 'frozen-rtl/replay-result.json')
    if not result['valid'] or result['rates'] != case['rates']:
        raise ValueError('frozen activity mismatch')
    rtl = next((out / 'frozen-rtl/cache' / result['cache_id']).glob('attempt-*'))
    waveform = restore(rtl / 'activity.vcd')
    gls = out / 'frozen-gls'
    provenance = read(gls / 'provenance.json')
    for name, digest in provenance['inputs'].items():
        if sha(Path(name)) != digest:
            raise ValueError(f'GLS input changed: {name}')
    if sha(gls / 'activity.vcd') != provenance['waveform_sha256']:
        raise ValueError('GLS waveform changed')
    if provenance['observed'] != read(rtl / 'sim_build/observed.json'):
        raise ValueError('GLS/frozen RTL observations differ')
    power = evaluate(gls / 'activity.vcd', waveform, synthesis, 'clk', 'axi_dma',
                     9216, out / 'power')
    fractions = [r['annotated_pins'] / (r['annotated_pins'] + r['unannotated_pins'])
                 for r in [power['full'], *power['windows']]]
    if len(power['windows']) != 8 or min(fractions) < .99:
        raise ValueError('window count or annotation requirement failed')
    paths = [out / 'selection.json', out / 'frozen-rtl/replay-receipt.json',
             out / 'frozen-rtl/replay-result.json', gls / 'provenance.json',
             out / 'power/power.json', Path(__file__), config.LIBERTY,
             synthesis / 'manifest.json', synthesis / 'yosys.log']
    receipt = dict(case_id=case['id'], plan_sha256=plan['sha256'],
                   frozen_runtime=str(runtime.resolve()), frozen_source_match=True,
                   exact_activity_match=True, rates=result['rates'],
                   reference_correctness=provenance['reference_checks'],
                   observed=provenance['observed'], clock='axi_dma.clk', scope='axi_dma',
                   grid=power['grid'], pin_annotation_fractions=fractions,
                   dynamic_power_w=[r['dynamic_power_w'] for r in power['windows']],
                   switching_additivity_pass=power['switching_additivity_pass'],
                   inputs={str(p.resolve()): sha(p) for p in paths},
                   claim='Selected frozen case; zero-delay mapped-gate power, not signoff.')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'runtime', 'synthesis', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--case', required=True)
    args = parser.parse_args()
    plan = read(args.plan)
    verify(plan)
    case = next(c for c in plan['cases'] if c['id'] == args.case)
    if case['domain'] != 'dma-temporal':
        raise ValueError('DMA case required')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'selection.json').write_text(json.dumps(plan, indent=2) + '\n')
    result = replay(case, read(Path(case['root']) / 'manifest.json'),
                    args.runtime, out / 'frozen-rtl')
    rtl = next((out / 'frozen-rtl/cache' / result['cache_id']).glob('attempt-*'))
    restore(rtl / 'activity.vcd')
    command = [sys.executable, '-m', 'agcws.designs.dma.gls', '--rtl', str(rtl),
               '--synthesis', str(args.synthesis.resolve()), '--out', str(out / 'frozen-gls')]
    subprocess.run(command, check=True, env=os.environ)
    print(json.dumps(finish(out, plan, case, args.synthesis.resolve(), args.runtime)))


if __name__ == '__main__':
    main()
