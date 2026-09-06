"""Check the pinned upstream window regression and record the installed binary."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PIN = 'a9a3f30ca97dc13f9ef911cae1a82c42c67379e1'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify(source, binary):
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != PIN:
        raise ValueError('unexpected upstream commit')
    if subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain'], text=True).strip():
        raise ValueError('upstream source tree must be clean')
    help_result = subprocess.run([str(binary), '-no_init'], input='help read_vcd\nexit\n',
                                 text=True, capture_output=True, check=True)
    if not all(flag in help_result.stdout for flag in ('-begin_time', '-end_time')):
        raise ValueError('binary lacks native window support')
    test_dir = source / 'test'
    run = subprocess.run([str(binary), '-no_init', '-exit', 'vcd_begin_end_time.tcl'],
                         cwd=test_dir, text=True, capture_output=True, check=True)
    marker = 'Annotated 2 pin activities.'
    if marker not in run.stdout or run.stderr.strip():
        raise ValueError('window regression did not run cleanly')
    observed = run.stdout[run.stdout.index(marker):].strip()
    if observed != (test_dir / 'vcd_begin_end_time.ok').read_text().strip():
        raise ValueError('window regression differs from upstream expected output')
    names = ('vcd_begin_end_time.tcl', 'vcd_begin_end_time.v',
             'vcd_begin_end_time.vcd', 'vcd_begin_end_time.ok', 'asap7_invbuf.lib.gz')
    return {'upstream': 'https://github.com/The-OpenROAD-Project/OpenSTA', 'commit': commit,
            'binary': str(binary), 'binary_sha256': sha(binary),
            'help': help_result.stdout, 'regression': 'exact_match',
            'fixture_sha256': {name: sha(test_dir / name) for name in names},
            'window_units': 'Integer ticks in the VCD timescale, not automatically nanoseconds.',
            'boundary_semantics': 'Transitions at both begin_time and end_time are included.',
            'limitation': 'This regression does not validate the study-wide temporal power profiles.'}, run.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result, log = verify(args.source.resolve(), args.binary.resolve())
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.out / 'window_regression.log').write_text(log)
    print('Verified pinned OpenSTA native window support and upstream regression')


if __name__ == '__main__':
    main()
