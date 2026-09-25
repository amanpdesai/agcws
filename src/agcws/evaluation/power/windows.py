"""Versioned native-window power with event-free boundaries and raw reports."""
import argparse
import itertools
import json
import math
import re
import subprocess
import time
from pathlib import Path

from agcws.core import config
from agcws.designs.aes.gls import sha
from agcws.evaluation.power.parse import parse_report
from agcws.evaluation.power.verify_windows import PIN
from agcws.evaluation.waveforms.grid import grid
from agcws.evaluation.waveforms.span import UNITS

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


def aligned_grids(left, right, marker_bounded=False):
    if not marker_bounded:
        return {k: v for k, v in left.items() if k != 'clock'} == {
            k: v for k, v in right.items() if k != 'clock'}
    keys = ('clock_edges', 'clock_period_ticks', 'edge_indices', 'durations_ticks',
            'durations_s', 'relative_edges_sha256')
    return (left['span']['timescale_s'] == right['span']['timescale_s']
            and all(left[k] == right[k] for k in keys))


def reconstruction(full, weighted, *, policy='strict', top=None, period_s=None, proof=None,
                   window_values=None, durations_s=None):
    if policy not in ('strict', 'slew-verified-v1'):
        raise ValueError('unknown reconstruction policy')
    approved = ('ibex_top', 'agcws_redmule_4x4')
    if policy != 'strict' and (top not in approved or period_s != 1e-8):
        raise ValueError('qualified reconstruction requires an approved design at 10 ns')
    if not all(math.isfinite(x) and x >= 0 for x in (full, weighted)):
        raise ValueError('invalid switching reconstruction values')
    passed = math.isclose(weighted, full, rel_tol=1e-5, abs_tol=1e-12)
    verified = False
    if policy == 'slew-verified-v1' and proof is not None:
        from agcws.evaluation.power.reconstruction_audit import VERIFIED_CHECKS
        try:
            values, durations = proof['native_windows_w'], proof['durations_s']
            residual, explained = proof['unexplained_difference_w'], proof['explained_difference_w']
            shape_ok = (len(values) == len(durations) > 0
                        and all(math.isfinite(v) and v >= 0 for v in values)
                        and all(math.isfinite(d) and d > 0 for d in durations))
            verified = (shape_ok and proof.get('version') == policy and proof.get('pass') is True
                    and proof.get('failures') == []
                    and proof.get('verified_checks') == list(VERIFIED_CHECKS)
                    and proof.get('count_mismatch_count') == 0
                    and proof['counted_pins'] > 0 and proof['output_pins'] > 0
                    and len(proof['report_sha256']) == len(values)+1
                    and all(re.fullmatch('[0-9a-f]{64}', h) for h in proof['report_sha256'].values())
                    and math.isfinite(residual) and math.isfinite(explained)
                    and abs(residual) <= max(1e-12, 1e-5 * full)
                    and math.isclose(weighted-full, residual+explained, rel_tol=1e-5, abs_tol=1e-12)
                    and math.isclose(math.fsum(v*d for v, d in zip(values, durations))/math.fsum(durations),
                                     weighted, rel_tol=1e-12, abs_tol=1e-15)
                    and (window_values is None or values == window_values)
                    and (durations_s is None or durations == durations_s)
                    and math.isclose(proof.get('native_full_w', math.nan), full,
                                     rel_tol=1e-12, abs_tol=1e-15)
                    and math.isclose(proof.get('native_weighted_w', math.nan), weighted,
                                     rel_tol=1e-12, abs_tol=1e-15))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            verified = False
    accepted = verified if policy == 'slew-verified-v1' else passed
    return {'policy': policy, 'pass': passed,
            'absolute_error_w': abs(weighted-full),
            'relative_error': abs(weighted-full)/full if full else None,
            'accepted_estimate': accepted,
            **({'validation_pass': verified, 'proof': proof} if policy == 'slew-verified-v1' else {})}


def evaluate(waveform, rtl_waveform, synthesis, clock, scope, expected_edges, out,
             *, rtl_clock=None, bounds=None, rtl_bounds=None, expected_period_s=None, clock_port=None,
             reconstruction_policy='strict'):
    if reconstruction_policy == 'ibex-10ns-estimate-v1':
        raise ValueError('legacy estimate policy is archival only; use strict or slew-verified-v1')
    clock_port = clock_port or clock.split('.')[-1]
    for name in (clock, scope, clock_port):
        if not re.fullmatch(r'[A-Za-z0-9_/.]+', name):
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
    if rtl_bounds is not None and bounds is None:
        raise ValueError('separate RTL bounds require GLS marker bounds')
    options = {} if bounds is None else dict(begin=bounds[0], end=bounds[1])
    rtl_options = options if rtl_bounds is None else dict(begin=rtl_bounds[0], end=rtl_bounds[1])
    left = grid(rtl_waveform, rtl_clock or clock, expected_edges, **rtl_options)
    right = grid(waveform, clock, expected_edges, **options)
    if not aligned_grids(left, right, marker_bounded=bounds is not None):
        raise ValueError('RTL/GLS measurement grids differ')
    period_s = right['clock_period_ticks'] * right['span']['timescale_s']
    reconstruction(0, 0, policy=reconstruction_policy, top=top, period_s=period_s)
    if expected_period_s is not None and not math.isclose(period_s, expected_period_s, rel_tol=1e-12):
        raise ValueError('waveform clock period differs from declared design clock')
    units = re.findall(r'\btime_unit\s*:\s*"([0-9.]+)\s*(s|ms|us|ns|ps|fs)"', config.LIBERTY.read_text())
    if len(units) != 1:
        raise ValueError('Liberty must declare exactly one time unit')
    period_ui = period_s / (float(units[0][0]) * UNITS[units[0][1]])
    if reconstruction_policy == 'slew-verified-v1':
        from agcws.evaluation.power.reconstruction_audit import LIBERTY_SHA256
        if sha(config.LIBERTY) != LIBERTY_SHA256:
            raise ValueError('unsupported Liberty for slew-verified-v1')
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    prefix = (f'read_liberty {quoted(config.LIBERTY)}\nread_verilog {quoted(synthesis / "mapped.v")}\n'
              f'link_design {top}\ncreate_clock -period {period_ui:.17g} [get_ports {clock_port}]\n')
    cuts = right['bounds_ticks']
    ranges = [('full', cuts[0], cuts[-1]), *[(f'bin-{i}', a, b) for i, (a,b) in enumerate(itertools.pairwise(cuts))]]
    rows, artifacts = [], {}
    for name, begin, end in ranges:
        tcl = out / f'{name}.tcl'
        script = (prefix + f'read_vcd -scope {scope} -begin_time {begin} -end_time {end} {quoted(waveform)}\n'
                  + 'report_power -digits 12\nreport_activity_annotation -report_unannotated\n'
                  + LEAF_SUM_TCL)
        if reconstruction_policy == 'slew-verified-v1':
            from agcws.evaluation.power.reconstruction_audit import instrument_tcl
            script = instrument_tcl(script)
        tcl.write_text(script)
        report = out / f'{name}.rpt'
        with report.open('w') as log:
            subprocess.run([str(tool), '-no_init', '-exit', str(tcl)], stdout=log, stderr=subprocess.STDOUT, check=True)
        with report.open() as stream:
            text = ''.join(line for line in stream
                           if not line.startswith(('read_vcd:', 'SLEW_')))
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
    proof = None
    if reconstruction_policy == 'slew-verified-v1':
        from agcws.evaluation.power.reconstruction_audit import slew_proof
        try:
            proof = slew_proof([out / f'{r[0]}.rpt' for r in ranges],
                               right['durations_s'], rows)
        except ValueError as error:
            proof = {'version': reconstruction_policy, 'pass': False, 'failures': [str(error)]}
        (out / 'slew-proof.json').write_text(json.dumps(proof, indent=2)+'\n')
        artifacts['slew-proof.json'] = sha(out / 'slew-proof.json')
    diagnostic = reconstruction(full['leaf_switching_sum_w'], leaf_weighted,
                                policy=reconstruction_policy, top=top, period_s=period_s, proof=proof,
                                window_values=[r['leaf_switching_sum_w'] for r in bins],
                                durations_s=right['durations_s'])
    switching_ok = diagnostic['pass']
    paths = [waveform, rtl_waveform, synthesis/'mapped.v', synthesis/'manifest.json', config.LIBERTY, tool,
             Path(__file__), Path('src/agcws/evaluation/waveforms/grid.py')]
    if reconstruction_policy == 'slew-verified-v1':
        from agcws.evaluation.power import reconstruction_audit
        paths.append(Path(reconstruction_audit.__file__))
    result = {'scope': 'Selected-case native-window validation, not new search or superiority inference.',
              'grid': right, 'rtl_grid': left, 'clock_period_s': period_s,
              'alignment': 'relative marker window' if bounds is not None else 'whole waveform',
              'tool_version': version, 'inputs': {str(p): sha(p) for p in paths},
              'full': full, 'windows': bins, 'weighted_means': weighted,
              'weighted_leaf_switching_w': leaf_weighted,
              'switching_additivity_pass': switching_ok, 'artifact_sha256': artifacts,
              'switching_reconstruction': diagnostic,
              'wall_clock_s': time.monotonic()-start}
    (out/'power.json').write_text(json.dumps(result, indent=2)+'\n')
    if not diagnostic['accepted_estimate']:
        raise ValueError('switching additivity failed; retain diagnostic reports')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    for name in ('waveform', 'rtl-waveform', 'synthesis', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--clock', required=True)
    parser.add_argument('--scope', required=True)
    parser.add_argument('--expected-edges', type=int, required=True)
    parser.add_argument('--reconstruction-policy', default='strict',
                        choices=('strict', 'slew-verified-v1'))
    args = parser.parse_args(argv)
    evaluate(args.waveform, args.rtl_waveform, args.synthesis, args.clock, args.scope,
             args.expected_edges, args.out, reconstruction_policy=args.reconstruction_policy)
    print('WINDOW_POWER_VERIFIED', args.out, flush=True)


if __name__ == '__main__':
    main()
