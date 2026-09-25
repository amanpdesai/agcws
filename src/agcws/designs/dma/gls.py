"""Replay a fixed-horizon DMA trial on mapped gates using its original harness."""
import argparse
import json
import os
import subprocess
from pathlib import Path

from agcws.core import config
from agcws.designs.aes.gls import sha
from agcws.designs.assets import asset_path
from agcws.evaluation.activity.generic import parse_vcd
from agcws.evaluation.waveforms.grid import grid


def validate_inputs(rtl, synthesis):
    """Reject unverifiable gates and stale replay inputs before simulation."""
    mapped = json.loads((synthesis / 'manifest.json').read_text())
    expected = {str(Path('benchmarks/verilog-axi/rtl') / name)
                for name in ('axi_dma.v', 'axi_dma_rd.v', 'axi_dma_wr.v')}
    if set(mapped.get('sources', {})) != expected:
        raise ValueError('DMA synthesis requires the complete RTL source inventory; regenerate it')
    if any(sha(Path(p)) != digest for p, digest in mapped['sources'].items()):
        raise ValueError('synthesized DMA RTL sources differ from this checkout')
    if mapped.get('memory_manifest') or mapped.get('memory_libmap'):
        raise ValueError('macro-mapped DMA requires a separately validated driver')
    if mapped['top'] != 'axi_dma' or mapped['netlist_sha256'] != sha(synthesis / 'mapped.v'):
        raise ValueError('mapped DMA netlist checksum/top mismatch')
    if mapped['liberty_sha256'] != sha(config.LIBERTY):
        raise ValueError('configured Liberty differs from mapped DMA library')
    manifest = json.loads((rtl / 'manifest.json').read_text())
    if manifest.get('backend') != 'axi_dma_pipelined_tb':
        raise ValueError('DMA GLS requires the reference-checked pipelined harness')
    for name, field in [('workload.json', 'workload_sha256'),
                        ('activity.json', 'activity_sha256'),
                        ('activity.vcd', 'waveform_sha256')]:
        if sha(rtl / name) != manifest[field]:
            raise ValueError(f'RTL replay input differs: {name}')
    return mapped


def main(argv=None):
    config._load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('--rtl', type=Path, required=True)
    parser.add_argument('--synthesis', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    rtl, synthesis, out = args.rtl.resolve(), args.synthesis.resolve(), args.out.resolve()
    original = json.loads((rtl / 'sim_build/observed.json').read_text())
    activity = json.loads((rtl / 'activity.json').read_text())
    mapped = validate_inputs(rtl, synthesis)
    if original['observation_cycles'] != activity['clock_edges']:
        raise ValueError('RTL observation-window mismatch')
    cells = Path(os.environ['AGCWS_SKY130_CELL_MODELS']).resolve(strict=True)
    primitives = Path(os.environ['AGCWS_SKY130_PRIMITIVES']).resolve(strict=True)
    harness = asset_path('dma', 'axi_dma_pipelined_tb.py')
    helper = harness.with_name('axi_dma_coupled_tb.py')
    paths = [synthesis / 'mapped.v', synthesis / 'manifest.json', config.LIBERTY,
             cells, primitives, harness, helper, Path(__file__).resolve(),
             rtl / 'workload.json', rtl / 'manifest.json', rtl / 'activity.json',
             rtl / 'activity.vcd', rtl / 'sim_build/observed.json',
             *map(Path, mapped['sources'])]
    inputs = {str(path.resolve()): sha(path) for path in paths}
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env.pop('AGCWS_GLS_DIAGNOSTIC', None)
    env.update(AGCWS_DMA_WORKLOAD=str(rtl / 'workload.json'),
               AGCWS_DMA_OBSERVATION_CYCLES=str(original['observation_cycles']),
               AGCWS_DMA_TRAILING_IDLE=str(original['trailing_idle_cycles']),
               PYTHONPATH=str(harness.parent) + os.pathsep + str(Path(__file__).resolve().parents[3])
               + os.pathsep + env.get('PYTHONPATH', ''))
    command = (
        'from cocotb_test.simulator import run; import sys; '
        'run(verilog_sources=sys.argv[1:4], toplevel="axi_dma", '
        'module="axi_dma_pipelined_tb", simulator="icarus", waves=True, '
        'compile_args=["-DFUNCTIONAL", "-DUNIT_DELAY="], sim_build=sys.argv[4])'
    )
    with (out / 'driver.log').open('w') as log:
        subprocess.run([os.sys.executable, '-c', command, str(synthesis / 'mapped.v'),
                        str(cells), str(primitives), str(out / 'sim_build')],
                       env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    waveforms = list((out / 'sim_build').glob('*.fst'))
    if len(waveforms) != 1:
        raise ValueError('expected exactly one GLS waveform')
    with (out / 'activity.vcd').open('w') as waveform:
        subprocess.run([str(config.FST2VCD), str(waveforms[0])], stdout=waveform, check=True)
    observed = json.loads((out / 'sim_build/observed.json').read_text())
    if observed != original:
        raise ValueError(f'GLS timing/completion observations differ: {observed} != {original}')
    # Flop-mapped storage has uninitialized internal bits. This legacy transition
    # diagnostic is not the frozen RTL known-bit activity contract or its rates.
    measured = parse_vcd(out / 'activity.vcd', 'clk', 8, scope_prefix='axi_dma')
    if measured['clock_edges'] != activity['clock_edges']:
        raise ValueError('GLS observation window differs')
    (out / 'activity.json').write_text(json.dumps(measured) + '\n')
    rtl_grid = grid(rtl / 'activity.vcd', 'clk', original['observation_cycles'])
    gate_grid = grid(out / 'activity.vcd', 'clk', original['observation_cycles'])
    if rtl_grid != gate_grid:
        raise ValueError('RTL/GLS clock grids differ')
    if inputs != {str(path.resolve()): sha(path) for path in paths}:
        raise ValueError('DMA replay inputs changed during simulation')
    (out / 'provenance.json').write_text(json.dumps({
        'claim': 'Reference-checked, identical-observation DMA GLS replay; not a power report.',
        'inputs': inputs,
        'reference_checks': 'read bytes, destination bytes, descriptor tags/errors/counts; identical observed.json',
        'clock': 'axi_dma.clk', 'scope': 'axi_dma', 'grid': gate_grid,
        'activity_semantics': 'GLS transition diagnostic only; frozen RTL rates are validated separately',
        'compile_args': ['-DFUNCTIONAL', '-DUNIT_DELAY='],
        'synthesis': mapped,
        'observed': observed, 'clock_edges': measured['clock_edges'],
        'waveform_sha256': sha(out / 'activity.vcd'),
    }, indent=2) + '\n')
    print(f'DMA_MATCHED_GLS_DONE {out}', flush=True)


if __name__ == '__main__':
    main()
