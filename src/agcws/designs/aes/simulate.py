"""Replay the AES DSL with reference-checked transactions and measured coverage."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from agcws.core import config
from agcws.core.build import ensure_binary
from agcws.core.config import ROOT
from agcws.designs.aes.transactions import AESTransactionAdapter
from agcws.designs.assets import asset_path
from agcws.designs.validation import validate_static
from agcws.evaluation.activity.generic import parse_vcd
from agcws.evaluation.activity.known_bits import Observation, read_bits
from agcws.evaluation.simulation.coverage import read_line_coverage


def packed_state(data):
    return sum(data[4 * column + row] << (8 * (4 * row + column))
               for row in range(4) for column in range(4))


def compile_program(workload):
    validity = validate_static(AESTransactionAdapter(), workload)
    if not validity.valid:
        raise ValueError(validity.reason)
    lines = []
    bits = 128
    plain = bytes([int(workload.get('data_pattern', 0)) * 0x55]) + bytes(15)
    for op in workload['operations']:
        if op['op'] == 'configure':
            bits = op['key_len']
        elif op['op'] == 'idle':
            lines.append(f"0 {bits} {op['cycles']} 0 0")
        else:
            cipher = Cipher(algorithms.AES(bytes(bits // 8)), modes.ECB())
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(plain) + encryptor.finalize()
            inverse = op['op'] == 'decrypt'
            source, expected = (encrypted, plain) if inverse else (plain, encrypted)
            lines.extend([f'{2 if inverse else 1} {bits} 0 {packed_state(source):032x} '
                          f'{packed_state(expected):032x}'] * op['blocks'])
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('workload', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--bit-cycles', type=int, help='strict bit-activity observation horizon')
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    workload = json.loads(args.workload.read_text())
    program = out / 'program.txt'
    program.write_text(compile_program(workload))
    sources = subprocess.check_output([sys.executable, '-m', 'agcws.designs.aes.resolve_sources',
                                       '--top', 'aes_cipher_core'], text=True).split()
    harness = asset_path('aes', 'rtl.sv')
    driver = asset_path('aes', 'transactions.svh')
    version = subprocess.check_output([config.VERILATOR, '--version'])
    digest = hashlib.sha256(version + b'transactions-v1-coverage-line')
    headers = sorted((ROOT / 'benchmarks/opentitan/hw').rglob('*.svh'))
    # Macro include files are not listed by the module closure resolver.
    headers.extend(sorted((ROOT / 'benchmarks/opentitan/hw/ip/prim/rtl').glob('prim_assert*.sv')))
    for path in [*map(Path, sources), harness, driver, *headers]:
        digest.update(str(path).encode())
        digest.update(path.read_bytes())
    build = ROOT / 'out/.cache' / ('aes-transactions-' + digest.hexdigest()[:20])
    def compile_binary(binary):
        command = [config.VERILATOR, '--binary', '--trace-vcd', '--timing', '--sv',
                   '--coverage-line', '-DAGCWS_TRANSACTION_DRIVER', '--top-module', 'aes_core_smoke',
                   '-Wno-fatal', '-j', '2', '-Mdir', str(build), '-o', str(binary)]
        command.append('-I' + str(driver.parent))
        for directory in ['benchmarks/opentitan/hw/ip/aes/rtl',
                          'benchmarks/opentitan/hw/ip/prim/rtl',
                          'benchmarks/opentitan/hw/ip/prim_generic/rtl',
                          'benchmarks/opentitan/hw/ip/edn/rtl',
                          'benchmarks/opentitan/hw/ip/csrng/rtl',
                          'benchmarks/opentitan/hw/ip/entropy_src/rtl']:
            command.append('-I' + str(ROOT / directory))
        with (out / 'compile.log').open('w') as log:
            subprocess.run(command + sources + [str(harness)], stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    binary = ensure_binary(build, 'simulate', compile_binary)
    with (out / 'run.log').open('w') as log:
        subprocess.run([str(binary), '+PROGRAM=' + str(program),
                        '+verilator+coverage+file+' + str(out / 'coverage.dat')],
                       cwd=out, stdout=log, stderr=subprocess.STDOUT, check=True)
    if args.bit_cycles is not None:
        activity = read_bits(out / 'activity.vcd', Observation('aes_core_smoke.dut', 'aes_core_smoke.clk_i', args.bit_cycles))
    else:
        activity = parse_vcd(out / 'activity.vcd', 'clk_i', 8, scope_prefix='aes_core_smoke.dut')
    (out / 'activity.json').write_text(json.dumps(activity) + '\n')
    coverage = read_line_coverage(out / 'coverage.dat', ROOT, 'aes_core_smoke.dut')
    (out / 'coverage.json').write_text(json.dumps(coverage, sort_keys=True) + '\n')
    (out / 'provenance.json').write_text(json.dumps({
        'simulator_digest': digest.hexdigest(), 'verilator': version.decode().strip(),
        'workload_sha256': hashlib.sha256(args.workload.read_bytes()).hexdigest(),
        'backend': 'aes-transactions-v1', 'functional_reference': 'cryptography AES-ECB zero key',
        'reset_policy': 'once_per_workload', 'coverage': 'verilator_line'}, indent=2) + '\n')
    print(json.dumps({'output': str(out), 'clock_edges': activity['clock_edges']}))


if __name__ == '__main__':
    main()
