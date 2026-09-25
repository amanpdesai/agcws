"""Diagnostic control: run original Ibex RTL under the proposed GLS harness.

This is not a gate replay or power measurement. It isolates harness behavior
from synthesis when debugging the first retirement mismatch.
"""

import argparse
import shutil
from pathlib import Path

from agcws.core import config
from agcws.designs.ibex.gls import ASSETS, closure, run, system_harness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--closure', type=Path, required=True)
    parser.add_argument('--reference-gls', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources, includes, defines = closure(args.closure)
    simulation = []
    for source in sources:
        if source.name == 'ibex_simple_system.sv':
            target = out / source.name
            target.write_text(system_harness(source.read_text()))
            simulation.append(target)
        else:
            simulation.append(source)
    harness = (ASSETS / 'gls.sv').read_text()
    (out / 'control.sv').write_text(harness)
    for name in ('program.vmem', 'retirement.vmem'):
        shutil.copyfile(args.reference_gls / name, out / name)
    count = len((out / 'retirement.vmem').read_text().splitlines())
    build = out / 'obj'
    run([config.VERILATOR, '--binary', '--timing', '--trace-fst',
         '--top-module', 'ibex_gls', '--Mdir', build, '-j', '8', '-Wno-fatal',
         '--timescale', '1ps/1ps', '-DDISABLE_PRIM_CDC_RAND_DELAY',
         '--unroll-count', '72', *[f'-D{k}={v}' for k, v in defines.items()],
         *[f'-I{p}' for p in includes], *simulation, out / 'control.sv'], out / 'compile.log')
    run([build / 'Vibex_gls', f'+RETIREMENTS={count}'], out / 'run.log', cwd=out)


if __name__ == '__main__':
    main()
