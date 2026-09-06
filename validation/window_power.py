"""Versioned native-window power with event-free boundaries and raw reports."""
import argparse
import itertools
import json
import math
import re
import subprocess
import time
from pathlib import Path

from agcws import config
from analysis.matched_power import parse_report
from maintenance.verify_opensta_windows import PIN
from validation.aes_gls import sha
from validation.window_grid import grid

LEAF_SUM_TCL = '''
set leaf_switching 0.0
set leaf_count 0
foreach inst [sta::network_leaf_instances] {
    set values [sta::instance_power $inst [sta::cmd_scene]]
    set leaf_switching [expr {$leaf_switching + [lindex $values 1]}]
    incr leaf_count
}
puts "LEAF_SWITCHING_SUM $leaf_count [format %.17g $leaf_switching]"
'''


def quoted(path):
    value = str(path.resolve(strict=True))
    if any(c in value for c in '{}\\\n\r'):
        raise ValueError('unsupported Tcl path characters')
    return '{' + value + '}'


def evaluate(waveform, rtl_waveform, synthesis, clock, scope, expected_edges, out):
    for name in (clock, scope):
        if not re.fullmatch(r'[A-Za-z0-9_/]+', name):
            raise ValueError('invalid clock/scope name')
    manifest = json.loads((synthesis / 'manifest.json').read_text())
    if sha(synthesis / 'mapped.v') != manifest['netlist_sha256'] or sha(config.LIBERTY) != manifest['liberty_sha256']:
        raise ValueError('mapped netlist or Liberty changed')
    top = manifest['top']
    if not re.fullmatch(r'[A-Za-z0-9_]+', top):
        raise ValueError('invalid top name')
    tool = config.OPENSTA.resolve(strict=True)
    version = subprocess.run([str(tool), '-no_init'], input='exit\n', text=True,
                             capture_output=True, check=True).stdout.splitlines()[0]
    if PIN[:10] not in version:
        raise ValueError('unexpected OpenSTA revision')
    left, right = grid(rtl_waveform, clock, expected_edges), grid(waveform, clock, expected_edges)
    if left != right:
        raise ValueError('RTL/GLS measurement grids differ')
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    prefix = (f'read_liberty {quoted(config.LIBERTY)}\nread_verilog {quoted(synthesis / "mapped.v")}\n'
              f'link_design {top}\ncreate_clock -period 10 [get_ports {clock}]\n')
    cuts = right['bounds_ticks']
    ranges = [('full', cuts[0], cuts[-1]), *[(f'bin-{i}', a, b) for i, (a,b) in enumerate(itertools.pairwise(cuts))]]
    rows, artifacts = [], {}
    for name, begin, end in ranges:
        tcl = out / f'{name}.tcl'
        tcl.write_text(prefix + f'read_vcd -scope {scope} -begin_time {begin} -end_time {end} {quoted(waveform)}\n'
                       'report_power -digits 12\nreport_activity_annotation -report_unannotated\n' + LEAF_SUM_TCL)
        report = out / f'{name}.rpt'
        with report.open('w') as log:
            subprocess.run([str(tool), '-no_init', '-exit', str(tcl)], stdout=log, stderr=subprocess.STDOUT, check=True)
        text = report.read_text()
        if re.search(r'^Error:', text, re.MULTILINE):
            raise ValueError('OpenSTA reported an error')
        power = parse_report(text)
        match = re.search(r'^LEAF_SWITCHING_SUM (\d+) ([0-9.eE+-]+)$', text, re.MULTILINE)
        if not match or int(match[1]) <= 0 or not math.isfinite(float(match[2])):
            raise ValueError('missing/nonfinite per-leaf switching sum')
        power.update(leaf_count=int(match[1]), leaf_switching_sum_w=float(match[2]))
        rows.append({'name': name, 'begin_tick': begin, 'end_tick': end, **power})
        artifacts.update({p.name: sha(p) for p in (tcl, report)})
    full, bins = rows[0], rows[1:]
    if any((r['annotated_pins'], r['unannotated_pins']) != (full['annotated_pins'], full['unannotated_pins']) for r in bins):
        raise ValueError('annotation coverage differs across windows')
    durations = right['durations_ticks']
    weighted = {key: sum(d*r[key] for d,r in zip(durations,bins))/sum(durations)
                for key in ('switching_power_w', 'internal_power_w', 'dynamic_power_w')}
    if any(r['leaf_count'] != full['leaf_count'] for r in bins):
        raise ValueError('leaf count differs across windows')
    leaf_weighted = math.fsum(d*r['leaf_switching_sum_w'] for d,r in zip(durations,bins))/sum(durations)
    switching_ok = math.isclose(leaf_weighted, full['leaf_switching_sum_w'], rel_tol=1e-5, abs_tol=1e-12)
    paths = [waveform, rtl_waveform, synthesis/'mapped.v', synthesis/'manifest.json', config.LIBERTY, tool,
             Path(__file__), Path('validation/window_grid.py'), Path('docs/WINDOWED_POWER_PROTOCOL.md')]
    result = {'scope': 'Selected-case native-window validation, not new search or superiority inference.',
              'grid': right, 'tool_version': version, 'inputs': {str(p): sha(p) for p in paths},
              'full': full, 'windows': bins, 'weighted_means': weighted,
              'weighted_leaf_switching_w': leaf_weighted,
              'switching_additivity_pass': switching_ok, 'artifact_sha256': artifacts,
              'wall_clock_s': time.monotonic()-start}
    (out/'power.json').write_text(json.dumps(result, indent=2)+'\n')
    if not switching_ok:
        raise ValueError('switching additivity failed; retain diagnostic reports')
    return result


def main():
    parser = argparse.ArgumentParser()
    for name in ('waveform', 'rtl-waveform', 'synthesis', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--clock', required=True)
    parser.add_argument('--scope', required=True)
    parser.add_argument('--expected-edges', type=int, required=True)
    args = parser.parse_args()
    evaluate(args.waveform, args.rtl_waveform, args.synthesis, args.clock, args.scope, args.expected_edges, args.out)
    print('WINDOW_POWER_VERIFIED', args.out, flush=True)


if __name__ == '__main__':
    main()
