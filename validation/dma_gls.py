"""Replay a fixed-horizon DMA trial on mapped gates using its original harness."""
import argparse
import json
import os
import subprocess
from pathlib import Path

from agcws import config
from agcws.nodes.activity import parse_vcd
from validation.aes_gls import sha


def main():
    config._load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('--rtl', type=Path, required=True)
    parser.add_argument('--synthesis', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rtl, synthesis, out = args.rtl.resolve(), args.synthesis.resolve(), args.out.resolve()
    original = json.loads((rtl / 'sim_build/observed.json').read_text())
    activity = json.loads((rtl / 'activity.json').read_text())
    mapped = json.loads((synthesis / 'manifest.json').read_text())
    if mapped['top'] != 'axi_dma' or mapped['netlist_sha256'] != sha(synthesis / 'mapped.v'):
        raise ValueError('mapped DMA netlist checksum/top mismatch')
    if original['observation_cycles'] != activity['clock_edges']:
        raise ValueError('RTL observation-window mismatch')
    cells = Path(os.environ['AGCWS_SKY130_CELL_MODELS']).resolve(strict=True)
    primitives = Path(os.environ['AGCWS_SKY130_PRIMITIVES']).resolve(strict=True)
    harness = Path('third_party/harnesses/axi_dma_pipelined_tb.py').resolve()
    helper = harness.with_name('axi_dma_coupled_tb.py')
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env.pop('AGCWS_GLS_DIAGNOSTIC', None)
    env.update(AGCWS_DMA_WORKLOAD=str(rtl / 'workload.json'),
               AGCWS_DMA_OBSERVATION_CYCLES=str(original['observation_cycles']),
               AGCWS_DMA_TRAILING_IDLE=str(original['trailing_idle_cycles']),
               PYTHONPATH=str(harness.parent) + os.pathsep + str(Path('src').resolve())
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
    measured = parse_vcd(out / 'activity.vcd', 'clk', 8)
    if measured['clock_edges'] != activity['clock_edges']:
        raise ValueError('GLS observation window differs')
    (out / 'activity.json').write_text(json.dumps(measured) + '\n')
    paths = [synthesis / 'mapped.v', cells, primitives, harness, helper,
             Path(__file__).resolve(), rtl / 'workload.json']
    (out / 'provenance.json').write_text(json.dumps({
        'scope': 'Reference-checked, identical-observation DMA GLS replay; not a power report.',
        'inputs': {str(path): sha(path) for path in paths},
        'observed': observed, 'clock_edges': measured['clock_edges'],
        'waveform_sha256': sha(out / 'activity.vcd'),
    }, indent=2) + '\n')
    print(f'DMA_MATCHED_GLS_DONE {out}', flush=True)


if __name__ == '__main__':
    main()
