"""Replay the AES DSL with reference-checked transactions and measured coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from agcws import config
from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.nodes.activity import parse_vcd
from agcws.nodes.validation import validate_static
from agcws.nodes.coverage import read_line_coverage


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('workload', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    workload = json.loads(args.workload.read_text())
    program = out / 'program.txt'
    program.write_text(compile_program(workload))
    sources = subprocess.check_output([sys.executable, 'scripts/resolve_sv_sources.py',
                                       '--top', 'aes_cipher_core'], text=True).split()
    harness = ROOT / 'experiments/aes_core_smoke.sv'
    driver = ROOT / 'experiments/aes_transactions.svh'
    version = subprocess.check_output([config.VERILATOR, '--version'])
    digest = hashlib.sha256(version + b'transactions-v1-coverage-line')
    for path in [*map(Path, sources), harness, driver]:
        digest.update(str(path).encode())
        digest.update(path.read_bytes())
    build = ROOT / 'out/.cache' / ('aes-transactions-' + digest.hexdigest()[:20])
    binary = build / 'simulate'
    if not binary.exists():
        build.mkdir(parents=True, exist_ok=True)
        command = [config.VERILATOR, '--binary', '--trace-vcd', '--timing', '--sv',
                   '--coverage-line', '-DAGCWS_TRANSACTION_DRIVER', '--top-module', 'aes_core_smoke',
                   '-Wno-fatal', '-j', '2', '-Mdir', str(build), '-o', str(binary)]
        for directory in ['experiments', 'third_party/opentitan/hw/ip/aes/rtl',
                          'third_party/opentitan/hw/ip/prim/rtl',
                          'third_party/opentitan/hw/ip/prim_generic/rtl',
                          'third_party/opentitan/hw/ip/edn/rtl',
                          'third_party/opentitan/hw/ip/csrng/rtl',
                          'third_party/opentitan/hw/ip/entropy_src/rtl']:
            command.append('-I' + str(ROOT / directory))
        with (out / 'compile.log').open('w') as log:
            subprocess.run(command + sources + [str(harness)], stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    with (out / 'run.log').open('w') as log:
        subprocess.run([str(binary), '+PROGRAM=' + str(program),
                        '+verilator+coverage+file+' + str(out / 'coverage.dat')],
                       cwd=out, stdout=log, stderr=subprocess.STDOUT, check=True)
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
