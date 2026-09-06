"""Independently check native-window transition density and carried-in duty."""
import argparse
import itertools
import json
import math
import re
import subprocess
from pathlib import Path

from agcws import config
from validation.aes_gls import sha
from validation.window_grid import grid
from validation.window_power import quoted

EVENTS = [(0, 0), (25, 1), (60, 0), (120, 1), (150, 0)]


def expected(begin, end):
    transitions = sum(begin <= tick <= end for tick, _ in EVENTS[1:])
    high = sum(max(0, min(end,b)-max(begin,a)) for a,b in ((25,60),(120,150)))
    return transitions, high/(end-begin)


def check(source, out):
    out.mkdir(parents=True, exist_ok=False)
    tool = config.OPENSTA.resolve(strict=True)
    rows = []
    for scale in (1, 10):
        path = out / f'toy-{scale}ps.vcd.txt'
        header = (f'$timescale {scale}ps $end\n$scope module top $end\n'
                  '$var wire 1 ! clk $end\n$var wire 1 " A $end\n$var wire 1 # Y $end\n'
                  '$upscope $end\n$enddefinitions $end\n#0\n0!\n0"\n1#\n')
        changes = dict(EVENTS[1:])
        body = ''
        for tick in range(5, 161, 5):
            body += f'#{tick}\n{int(tick % 10 == 5)}!\n'
            if tick in changes:
                body += f'{changes[tick]}"\n{1-changes[tick]}#\n'
        path.write_text(header+body)
        layout = grid(path, 'clk', 16)
        bounds = layout['bounds_ticks']
        tcl = out / f'toy-{scale}ps.tcl'
        text = (f'read_liberty {quoted(source / "test/asap7_invbuf.lib.gz")}\n'
                f'read_verilog {quoted(source / "test/vcd_begin_end_time.v")}\n'
                f'link_design top\ncreate_clock -period {10*scale} [get_ports clk]\n')
        for i,(begin,end) in enumerate(itertools.pairwise(bounds)):
            text += (f'sta::clear_power\nread_vcd -scope top -begin_time {begin} -end_time {end} {quoted(path)}\n'
                     f'puts "BIN {i} [get_property [get_pins u_inv/A] activity]"\n')
        tcl.write_text(text)
        run = subprocess.run([str(tool), '-no_init', '-exit', str(tcl)], text=True, capture_output=True, check=True)
        (out/f'toy-{scale}ps.log').write_text(run.stdout+run.stderr)
        matches = re.findall(r'^BIN (\d+) (\S+) (\S+)', run.stdout, re.MULTILINE)
        if len(matches) != 8 or 'Error:' in run.stdout or run.stderr.strip():
            raise ValueError('native toy-window evaluation failed')
        for match,begin,end in zip(matches,bounds,bounds[1:]):
            count, duty = expected(begin,end)
            measured_count = float(match[1])*(end-begin)*scale*1e-12
            measured_duty = float(match[2])
            if not (math.isclose(measured_count,count,abs_tol=1e-5) and math.isclose(measured_duty,duty,abs_tol=1e-3)):
                raise ValueError('native counts/duty differ from independent interval arithmetic')
            rows.append({'scale_ps':scale, 'bin':int(match[0]), 'begin':begin, 'end':end,
                         'expected_transitions':count, 'measured_transitions':measured_count,
                         'expected_duty':duty, 'measured_duty':measured_duty})
        if sum(expected(a,b)[0] for a,b in itertools.pairwise(bounds)) != 4:
            raise ValueError('boundary counting is not additive')
    artifacts = {p.name:sha(p) for p in out.iterdir() if p.is_file()}
    result = {'independent_checks':rows, 'binary_sha256':sha(tool), 'artifact_sha256':artifacts,
              'source_sha256':sha(Path(__file__)), 'grid_source_sha256':sha(Path('validation/window_grid.py'))}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('INDEPENDENT_WINDOW_SEMANTICS_VERIFIED', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    check(args.source,args.out)
