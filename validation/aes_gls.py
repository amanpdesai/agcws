"""Explicit unmasked synthesis and reference-checked transaction GLS replay."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from agcws import config
from agcws.nodes.activity import parse_vcd
from scripts.run_aes_transactions import compile_program

PARAMETERS = {'SecMasking': 0, 'SecSBoxImpl': 'aes_pkg::SBoxImplLut', 'EntropyWidth': 32}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(command, log, cwd=None):
    with log.open('w') as stream:
        subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT, check=True)


def synthesize(out):
    plugin = Path(os.environ['AGCWS_SLANG_PLUGIN']).resolve(strict=True)
    liberty = Path(os.environ.get('AGCWS_LIBERTY',
                                  'third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib')).resolve(strict=True)
    sources = [Path(p).resolve(strict=True) for p in subprocess.check_output(
        [os.sys.executable, 'scripts/resolve_sv_sources.py', '--top', 'aes_cipher_core'], text=True).split()]
    includes = sorted({str(p.parent) for p in sources})
    paths = [str(plugin), str(liberty), str(out), *map(str, sources)]
    if any(any(c in p for c in ' ;"\n') for p in paths):
        raise ValueError('Yosys paths must not contain whitespace or command delimiters')
    frontend = f'plugin -i {plugin}; read_slang --top aes_cipher_core -D SYNTHESIS '
    frontend += ' '.join(f'-G {k}={v}' for k, v in PARAMETERS.items()) + ' '
    frontend += ' '.join('-I ' + p for p in includes) + ' ' + ' '.join(map(str, sources))
    command = (frontend + '; hierarchy -top aes_cipher_core; proc; opt; memory_map; opt; '
               f'techmap; opt; dfflibmap -liberty {liberty}; abc -liberty {liberty}; clean; '
               f'write_verilog -noattr -noexpr {out}/mapped.v; tee -o {out}/stat.json stat -json')
    (out / 'synthesis.ys').write_text(command + '\n')
    run([str(config.YOSYS), '-Q', '-T', '-s', str(out / 'synthesis.ys')], out / 'synthesis.log')
    with (out / 'mapped.v').open() as stream:
        header = ''.join(next(stream) for _ in range(80))
    if 'input [127:0] state_init_i;' not in header or 'output [127:0] state_o;' not in header:
        raise ValueError('unmasked state interface was not synthesized')
    manifest = {'top': 'aes_cipher_core', 'parameters': PARAMETERS,
                'netlist_sha256': sha(out / 'mapped.v'), 'liberty': str(liberty),
                'liberty_sha256': sha(liberty), 'plugin_sha256': sha(plugin),
                'sources': {str(p): sha(p) for p in sources},
                'yosys_version': subprocess.check_output([str(config.YOSYS), '-V'], text=True).strip()}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


def replay(args, out):
    synth = args.synthesis.resolve(strict=True)
    manifest = json.loads((synth / 'manifest.json').read_text())
    if manifest['parameters'] != PARAMETERS or sha(synth / 'mapped.v') != manifest['netlist_sha256']:
        raise ValueError('netlist configuration or hash mismatch')
    cells = Path(os.environ['AGCWS_SKY130_CELL_MODELS']).resolve(strict=True)
    primitives = Path(os.environ['AGCWS_SKY130_PRIMITIVES']).resolve(strict=True)
    harness = Path('validation/aes_transaction_gls.sv').resolve()
    driver = Path('experiments/aes_transactions.svh').resolve()
    inputs = {str(p): sha(p) for p in (synth / 'mapped.v', cells, primitives, harness, driver,
                                      Path(__file__).resolve())}
    iverilog = os.environ.get('AGCWS_IVERILOG', 'iverilog')
    version = subprocess.run([iverilog, '-V'], capture_output=True, text=True, check=True).stdout
    cache_key = hashlib.sha256(json.dumps({'inputs': inputs, 'version': version}, sort_keys=True).encode()).hexdigest()
    build = Path('out/.cache/aes-matched-gls') / cache_key
    build.mkdir(parents=True, exist_ok=True)
    executable = (build / 'simulate.vvp').resolve()
    if not executable.exists():
        pending = executable.with_suffix('.pending.vvp')
        run([iverilog, '-g2012', '-DFUNCTIONAL', '-DUNIT_DELAY=', '-I', str(driver.parent),
             '-s', 'aes_core_smoke', '-o', str(pending), str(synth / 'mapped.v'),
             str(cells), str(primitives), str(harness)], out / 'compile.log')
        pending.replace(executable)
    workload = json.loads(args.workload.read_text())
    program = out / 'program.txt'
    program.write_text(compile_program(workload))
    run([os.environ.get('AGCWS_VVP', 'vvp'), str(executable), '+PROGRAM=' + str(program)], out / 'run.log', out)
    expected = sum(op.get('blocks', 0) for op in workload['operations'])
    match = re.search(r'AES_CORE_WORKLOAD_DONE blocks=(\d+)', (out / 'run.log').read_text())
    if not match or int(match[1]) != expected:
        raise ValueError('GLS did not complete all reference-checked transactions')
    activity = parse_vcd(out / 'activity.vcd', 'clk_i', 8, scope_prefix='aes_core_smoke.dut')
    if activity['clock_edges'] != args.clock_edges:
        raise ValueError(f"GLS measurement window mismatch: {activity['clock_edges']} != {args.clock_edges}")
    (out / 'activity.json').write_text(json.dumps(activity) + '\n')
    (out / 'provenance.json').write_text(json.dumps({
        'scope': 'Reference-checked unmasked GLS, not yet a power report.',
        'parameters': PARAMETERS, 'inputs': inputs, 'cache_key': cache_key,
        'program_sha256': sha(program), 'workload_sha256': sha(args.workload),
        'waveform_sha256': sha(out / 'activity.vcd'), 'clock_edges': activity['clock_edges'],
        'blocks_checked': expected,
    }, indent=2) + '\n')


def main():
    config._load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['synthesize', 'replay'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--synthesis', type=Path)
    parser.add_argument('--workload', type=Path)
    parser.add_argument('--clock-edges', type=int)
    args = parser.parse_args()
    if args.stage == 'replay' and not (args.synthesis and args.workload and args.clock_edges):
        parser.error('replay requires synthesis, workload and expected clock edges')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if args.stage == 'synthesize':
        synthesize(out)
    else:
        replay(args, out)
    print(f'AES_MATCHED_GLS_{args.stage.upper()}_DONE {out}', flush=True)


if __name__ == '__main__':
    main()
