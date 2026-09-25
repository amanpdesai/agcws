"""Bounded Ibex diagnostics and the opt-in slew-verified-v1 validation contract.

Native power, the estimator, and archived measurements are never modified.
All replay and acceptance evidence is written into new versioned directories.
"""

import argparse
import concurrent.futures
import json
import math
import re
import subprocess
from pathlib import Path

from agcws.evaluation.power.parse import parse_report as parse_native_report
from agcws.evaluation.power.windows import quoted, reconstruction
from agcws.evidence.retention import file_digest

POLICY = 'slew-verified-v1'
LIBERTY_SHA256 = '92eb4e93a3d4c2563018ac81cdec2f02fdeaced9b39337ed5c141fa63e0ad8f8'
VERIFIED_CHECKS = ('exact_pin_counts', 'invariant_coverage_load_slew',
                   'slew_density_model', 'load_voltage_power_model',
                   'strict_unaffected_cells', 'explained_aggregate_residual',
                   'native_measurement_reproduced')

# Native calculation is completed before these queries. No activity or timing
# setting is modified. Net capacitance is in SI; slew properties are in ns in
# the pinned, single-Liberty Ibex configuration.
SLEW_TCL = '''
puts "SLEW_AUDIT_VERSION slew-verified-v1"
foreach inst [sta::network_leaf_instances] {
    set values [sta::instance_power $inst [sta::cmd_scene]]
    puts "SLEW_LEAF [get_full_name $inst] [format %.17g [lindex $values 1]]"
    set iter [$inst pin_iterator]
    while {[$iter has_next]} {
        set pin [$iter next]
        if {[get_property $pin direction] == "output"} {
            set net [$pin net]
            set caps "0 0"
            if {$net != "NULL"} {
                set caps "[$net capacitance [sta::cmd_scene] min] [$net capacitance [sta::cmd_scene] max]"
            }
            puts "SLEW_PIN [get_full_name $pin] [get_full_name $inst] [get_property $pin activity] [get_property $pin slew_min_rise] [get_property $pin slew_min_fall] [get_property $pin slew_max_rise] [get_property $pin slew_max_fall] $caps"
        }
    }
    $iter finish
}
puts "SLEW_AUDIT_END"
'''


def instrument_tcl(text):
    if text.count('read_vcd ') != 1 or text.count('report_power ') != 1:
        raise ValueError('one read_vcd/report_power required')
    return (text.replace('read_vcd ', 'sta::set_debug read_vcd 1\nread_vcd ')
            .replace('report_power ', 'sta::set_debug read_vcd 0\nreport_power ') + SLEW_TCL)


def read_slew_report(path):
    """Stream a report; memory depends on netlist size, never waveform length."""
    counts, leaves, pins = {}, {}, {}
    version = end = False
    native_lines = []
    total = None
    count_re = re.compile(r'^read_vcd: (\S+) transitions ([0-9.]+) activity ')
    with path.open() as stream:
        for line in stream:
            if line.startswith(('Total ', 'vcd ', 'unannotated ')):
                native_lines.append(line)
            if line.startswith('Error:'):
                raise ValueError('OpenSTA error in proof report')
            match = count_re.match(line)
            if match:
                pin, count = match.groups()
                if pin in counts:
                    raise ValueError('duplicate counted pin')
                counts[pin] = float(count)
            elif line.startswith('SLEW_LEAF '):
                _, name, value = line.split()
                if name in leaves:
                    raise ValueError('duplicate leaf')
                leaves[name] = float(value)
            elif line.startswith('SLEW_PIN '):
                fields = line.split()
                if len(fields) != 12 or fields[1] in pins:
                    raise ValueError('invalid/duplicate output pin')
                pins[fields[1]] = {'cell': fields[2], 'density': float(fields[3]),
                                  'origin': fields[5],
                                  'slews': tuple(map(float, fields[6:10])),
                                  'caps': tuple(map(float, fields[10:12]))}
            elif line.startswith('SLEW_AUDIT_VERSION '):
                version = line.strip() == f'SLEW_AUDIT_VERSION {POLICY}'
            elif line.startswith('SLEW_AUDIT_END'):
                end = True
            elif line.startswith('LEAF_SWITCHING_SUM '):
                _, count, value = line.split()
                total = (int(count), float(value))
    if not version or not end or not counts or not leaves or not pins or total is None:
        raise ValueError('incomplete slew proof')
    numeric = [*counts.values(), *leaves.values(), total[1]]
    for pin in pins.values():
        numeric.extend([pin['density'], *pin['slews'], *pin['caps']])
    if any(not math.isfinite(v) or v < 0 for v in numeric):
        raise ValueError('nonfinite/negative proof observation')
    if total[0] != len(leaves) or not math.isclose(
            math.fsum(leaves.values()), total[1], rel_tol=1e-12, abs_tol=1e-15):
        raise ValueError('leaf sum mismatch')
    return {'counts': counts, 'leaves': leaves, 'pins': pins, 'total': total[1],
            'native': parse_native_report(''.join(native_lines)) if native_lines else None}


def slew_proof(paths, durations_s, expected_rows):
    """Fail closed, holding only a baseline and one current report in memory.

    Native power is never corrected. Affected single-output cells must follow
    min(count/duration, 1/min_average_slew) with a fixed measured coefficient.
    Multi-output clipping and non-VCD clipping are unsupported, not accepted.
    """
    if len(paths) != len(durations_s)+1 or len(expected_rows) != len(paths):
        raise ValueError('proof window shape mismatch')
    if not durations_s or any(not math.isfinite(d) or d <= 0 for d in durations_s):
        raise ValueError('invalid proof durations')
    full = read_slew_report(paths[0])
    duration = math.fsum(durations_s)
    totals = dict.fromkeys(full['counts'], 0.0)
    weighted = dict.fromkeys(full['leaves'], 0.0)
    predicted = dict.fromkeys(full['leaves'], 0.0)
    outputs = {cell: [] for cell in full['leaves']}
    for name, pin in full['pins'].items():
        outputs[pin['cell']].append(name)
    affected, coefficients, full_predictions, evidence = set(), {}, {}, {}
    failures = []

    def fail(message):
        # Bound receipt size even for a broadly incompatible report.
        if len(failures) < 30:
            failures.append(message)

    for index, path in enumerate(paths):
        report = full if index == 0 else read_slew_report(path)
        seconds = duration if index == 0 else durations_s[index-1]
        row = expected_rows[index]
        for field in ('counts', 'leaves', 'pins'):
            if report[field].keys() != full[field].keys():
                raise ValueError(f'{field} coverage changes')
        if (len(report['counts']) != row['annotated_pins'] or row['unannotated_pins'] != 0
                or len(report['leaves']) != row['leaf_count']
                or not math.isclose(report['total'], row['leaf_switching_sum_w'],
                                    rel_tol=1e-12, abs_tol=1e-15)):
            raise ValueError('proof does not reproduce native measurement/coverage')
        if 'internal_power_w' in row:
            if report['native'] is None or any(report['native'][k] != row[k]
                                              for k in report['native']):
                raise ValueError('native power components differ from measurement')
        if index:
            for pin, count in report['counts'].items():
                totals[pin] += count
            for cell, power in report['leaves'].items():
                weighted[cell] += power * seconds / duration
        for name, pin in report['pins'].items():
            base = full['pins'][name]
            if any(pin[k] != base[k] for k in ('cell', 'slews', 'caps', 'origin')):
                fail(f'load/slew/coverage/origin changed: {name}')
            if name not in report['counts']:
                fail(f'output lacks counted activity: {name}')
                continue
            if pin['origin'] not in ('vcd', 'clock'):
                fail(f'unsupported activity origin: {name}')
                continue
            raw = report['counts'][name] / seconds
            slew = min(sum(pin['slews'][:2]), sum(pin['slews'][2:])) * .5e-9
            cap = 1/slew if slew > 0 else math.inf
            effective = min(raw, cap)
            clipped = raw > cap * (1+1e-5)
            cell = pin['cell']
            if clipped and pin['origin'] == 'vcd':
                affected.add(cell)
            if pin['origin'] == 'vcd' and not math.isclose(
                    effective, pin['density'], rel_tol=1e-5, abs_tol=1e-12):
                fail(f'density not explained by slew cap: {name}')
            if len(outputs[cell]) != 1:
                if clipped:
                    fail(f'unsupported multi-output clipping: {cell}')
                continue
            if pin['origin'] != 'vcd':
                continue
            power = report['leaves'][cell]
            if pin['density'] > 0:
                coefficient = power / pin['density']
                previous = coefficients.setdefault(cell, coefficient)
                if not math.isclose(previous, coefficient, rel_tol=1e-5, abs_tol=1e-24):
                    fail(f'switching coefficient changed: {cell}')
            elif power != 0:
                fail(f'nonzero switching at zero density: {cell}')
            # Independent physical coefficient from the measured load and
            # pinned single-voltage Liberty, not a fitted residual correction.
            model = .5 * pin['caps'][1] * 1.8**2 * effective
            if not math.isclose(model, power, rel_tol=1e-5, abs_tol=1e-12):
                fail(f'load/voltage/density does not explain native switching: {cell}')
            if index == 0:
                full_predictions[cell] = model
            else:
                predicted[cell] += model * seconds / duration
            if clipped or cell in affected:
                evidence.setdefault(cell, []).append({'window': index, 'pin': name,
                    'transitions': report['counts'][name], 'raw_density_hz': raw,
                    'effective_density_hz': pin['density'], 'density_cap_hz': cap,
                    'native_switching_w': power})
        if index:
            del report
    mismatch_count = sum(totals[p] != n for p, n in full['counts'].items())
    if mismatch_count:
        fail(f'nonadditive transition counts: {mismatch_count} pins')
    unexplained = []
    explained = []
    for cell, power in full['leaves'].items():
        delta = weighted[cell] - power
        if cell in affected:
            model_delta = predicted[cell] - full_predictions.get(cell, 0.0)
            explained.append(model_delta)
            residual = delta - model_delta
            if abs(residual) > max(1e-12, 1e-5 * abs(power)):
                fail(f'unexplained clipped-cell residual: {cell}')
        else:
            residual = delta
            if not math.isclose(weighted[cell], power, rel_tol=1e-5, abs_tol=1e-12):
                fail(f'nonadditive unaffected cell: {cell}')
        unexplained.append(residual)
    native_full = full['total']
    native_weighted = math.fsum(weighted.values())
    residual = math.fsum(unexplained)
    if abs(residual) > max(1e-12, 1e-5 * abs(native_full)):
        fail('unexplained aggregate residual')
    return {'version': POLICY, 'pass': not failures, 'failures': failures,
            'verified_checks': list(VERIFIED_CHECKS) if not failures else [],
            'counted_pins': len(full['counts']), 'output_pins': len(full['pins']),
            'count_mismatch_count': mismatch_count, 'native_full_w': native_full,
            'native_weighted_w': native_weighted,
            'native_windows_w': [r['leaf_switching_sum_w'] for r in expected_rows[1:]],
            'durations_s': durations_s,
            'explained_difference_w': math.fsum(explained), 'unexplained_difference_w': residual,
            'clipped_cells': sorted(affected), 'clipping_evidence': evidence,
            'clipped_cell_parameters': {cell: full['pins'][outputs[cell][0]]
                                        for cell in sorted(affected)},
            'voltage_v': 1.8,
            'contract': 'Exact counted activity; invariant output load/slew; strict unaffected cells; slew-explained native power nonadditivity. Not timing signoff.',
            'report_sha256': {str(p): file_digest(p)[0] for p in paths}}


def audit_archived(measurement, out, *, waveform=None, workers=3, resume=False, timeout_s=300):
    """Power-only replay of one immutable archived measurement into new files."""
    root = Path.cwd()
    original_hash = file_digest(measurement)[0]
    implementation_hash = file_digest(Path(__file__))[0]
    windows_hash = file_digest(Path(__file__).with_name('windows.py'))[0]
    document = json.loads(measurement.read_text())
    record = document['power']
    if record['clock_period_s'] != 1e-8 or len(record['windows']) != 8:
        raise ValueError('only pinned Ibex 10 ns eight-bin records supported')
    inputs = record['inputs']
    tool = root / 'out/tools/opensta-a9a3f30/bin/sta'
    liberty = root / 'benchmarks/support/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib'
    netlist = root / 'out/ibex-matched-gls-dev-v1/synthesis-frozen-12-v3/mapped.v'
    for path in (tool, netlist, netlist.parent / 'manifest.json'):
        if file_digest(path)[0] != inputs[str(path)]:
            raise ValueError(f'archived input changed: {path}')
    if file_digest(liberty)[0] != next(v for k, v in inputs.items() if k.endswith('.lib')):
        raise ValueError('archived Liberty changed')
    # This model's ns slew interpretation is intentionally pinned to this lib.
    if file_digest(liberty)[0] != LIBERTY_SHA256:
        raise ValueError('unsupported Liberty for slew proof')
    archived = json.loads((measurement.parent / 'power/power.json').read_text())
    if archived != record:
        raise ValueError('archived power.json differs from measurement')
    for name, digest in record['artifact_sha256'].items():
        if Path(name).name != name or file_digest(measurement.parent / 'power' / name)[0] != digest:
            raise ValueError(f'archived power artifact changed: {name}')
    out.mkdir(parents=True, exist_ok=resume)
    snapshot = out / 'measurement-snapshot.json'
    if snapshot.exists():
        if json.loads(snapshot.read_text()) != document:
            raise ValueError('resume measurement differs')
    else:
        snapshot.write_text(json.dumps(document, indent=2)+'\n')
    source = measurement.parent / 'gls/power_gls.vcd'
    wave_hash = inputs[str(source.resolve())]
    if waveform is None:
        waveform = out / 'power_gls.vcd'
        if source.is_file():
            waveform = source
        elif not (resume and waveform.is_file()):
            receipt = restore(source, waveform, wave_hash)
            (out / 'restore.json').write_text(json.dumps(receipt, indent=2)+'\n')
    if file_digest(waveform)[0] != wave_hash:
        raise ValueError('waveform hash mismatch')
    rows = [record['full'], *record['windows']]

    def run(row):
        name = row['name']
        source_tcl = measurement.parent / 'power' / f'{name}.tcl'
        script = source_tcl.read_text()
        if 'link_design ibex_top\n' not in script or 'create_clock -period 10 ' not in script:
            raise ValueError('unexpected archived timing/design')
        script = script.replace('third_party/liberty/', 'benchmarks/support/liberty/')
        script = script.replace('{' + str(source.resolve()) + '}', quoted(waveform))
        tcl, report = out / f'{name}.tcl', out / f'{name}.rpt'
        instrumented = instrument_tcl(script)
        checkpoint = out / f'{name}.checkpoint.json'
        if resume and checkpoint.is_file():
            saved = json.loads(checkpoint.read_text())
            if (tcl.read_text() != instrumented or file_digest(report)[0] != saved['report_sha256']
                    or file_digest(tcl)[0] != saved['tcl_sha256']):
                raise ValueError('resume report/Tcl changed')
            return report
        # Only incomplete diagnostic artifacts inside the new output directory
        # may be replaced; checkpointed evidence is immutable and hash checked.
        tcl.write_text(instrumented)
        with report.open('w' if resume else 'x') as stream:
            subprocess.run([str(tool), '-no_init', '-exit', str(tcl)],
                           stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=timeout_s)
        read_slew_report(report)
        checkpoint.write_text(json.dumps({'report_sha256': file_digest(report)[0],
                                          'tcl_sha256': file_digest(tcl)[0]})+'\n')
        print(f'{document["activity"]["target"]}: {name}', flush=True)
        return report

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        paths = list(executor.map(run, rows))
    try:
        proof = slew_proof(paths, record['grid']['durations_s'], rows)
    except ValueError as error:
        proof = {'version': POLICY, 'pass': False, 'failures': [str(error)]}
    if file_digest(measurement)[0] != original_hash:
        raise ValueError('measurement changed during audit')
    diagnostic = reconstruction(record['full']['leaf_switching_sum_w'],
                                record['weighted_leaf_switching_w'], policy=POLICY,
                                top='ibex_top', period_s=1e-8, proof=proof)
    result = {'version': POLICY, 'measurement': str(measurement.resolve()),
              'measurement_sha256': original_hash, 'target': document['activity']['target'],
              'source_inputs': inputs, 'waveform_sha256': wave_hash,
              'implementation_sha256': implementation_hash,
              'windows_implementation_sha256': windows_hash,
              'native_power': record, 'switching_reconstruction': diagnostic,
              'artifact_sha256': {p.name: file_digest(p)[0] for p in out.iterdir()
                                 if p.suffix in ('.rpt', '.tcl', '.json')}}
    (out / 'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    return {'target': result['target'], 'accepted': diagnostic['accepted_estimate'],
            'failures': proof['failures'], 'receipt': str(out / 'receipt.json')}


def reprove_receipt(receipt_path, out):
    """Recheck hash-verified saved evidence with the current proof implementation."""
    old = json.loads(receipt_path.read_text())
    measurement = Path(old['measurement'])
    if file_digest(measurement)[0] != old['measurement_sha256']:
        raise ValueError('archived measurement changed')
    record = json.loads(measurement.read_text())['power']
    if record != old['native_power']:
        raise ValueError('receipt native power differs from archived measurement')
    for name, digest in record['inputs'].items():
        if name.endswith(('/sta', '/mapped.v', '/manifest.json', '.lib')):
            path = Path(name.replace('third_party/liberty/', 'benchmarks/support/liberty/'))
            if file_digest(path)[0] != digest:
                raise ValueError('archived model input changed')
    if next(v for k, v in record['inputs'].items() if k.endswith('.lib')) != LIBERTY_SHA256:
        raise ValueError('unsupported archived Liberty')
    for name, digest in old['artifact_sha256'].items():
        if Path(name).name != name or file_digest(receipt_path.parent / name)[0] != digest:
            raise ValueError('saved evidence hash mismatch')
    rows = [record['full'], *record['windows']]
    evidence_dir = Path(old.get('evidence_directory', receipt_path.parent.resolve()))
    paths = [evidence_dir / f'{r["name"]}.rpt' for r in rows]
    recorded_hashes = old['switching_reconstruction']['proof']['report_sha256']
    for path in paths:
        # Initial receipts may use relative keys; always resolve before matching.
        matches = [value for key, value in recorded_hashes.items()
                   if Path(key).resolve() == path.resolve()]
        if len(matches) != 1 or file_digest(path)[0] != matches[0]:
            raise ValueError('proof report hash mismatch')
    proof = slew_proof(paths, record['grid']['durations_s'], rows)
    diagnostic = reconstruction(record['full']['leaf_switching_sum_w'],
                                record['weighted_leaf_switching_w'], policy=POLICY,
                                top='ibex_top', period_s=record['clock_period_s'], proof=proof)
    result = dict(old, switching_reconstruction=diagnostic,
                  evidence_directory=str(evidence_dir.resolve()),
                  parent_receipt=str(receipt_path.resolve()),
                  parent_receipt_sha256=file_digest(receipt_path)[0],
                  implementation_sha256=file_digest(Path(__file__))[0],
                  windows_implementation_sha256=file_digest(Path(__file__).with_name('windows.py'))[0])
    out.mkdir(parents=True, exist_ok=False)
    result['artifact_sha256'] = {}
    (out / 'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    return {'target': result['target'], 'accepted': diagnostic['accepted_estimate'],
            'failures': proof['failures'], 'receipt': str(out / 'receipt.json')}


def finalize_batch(measurements, replay_root, out):
    """Create immutable, current-policy receipts and a small batch index."""
    out.mkdir(parents=True, exist_ok=False)
    snapshots = {}
    for source in (Path(__file__), Path(__file__).with_name('windows.py'),
                   Path(__file__).with_name('finalists.py'),
                   Path(__file__).parents[2] / 'reporting/power_reference.py'):
        destination = out / f'source-{source.name}'
        destination.write_bytes(source.read_bytes())
        snapshots[source.name] = file_digest(destination)[0]
    results = []
    for measurement in measurements:
        document = json.loads(measurement.read_text())
        target = document['activity']['target']
        old_path = replay_root / target / 'receipt.json'
        old = json.loads(old_path.read_text())
        if old['measurement_sha256'] != file_digest(measurement)[0]:
            raise ValueError('batch source differs from replay measurement')
        result = reprove_receipt(old_path, out / target)
        final = json.loads(Path(result['receipt']).read_text())
        proof = final['switching_reconstruction']['proof']
        result.update(native_additivity_pass=final['switching_reconstruction']['pass'],
                      native_relative_error=final['switching_reconstruction']['relative_error'],
                      count_mismatch_count=proof['count_mismatch_count'],
                      unexplained_difference_w=proof['unexplained_difference_w'],
                      clipped_cells=proof['clipped_cells'],
                      receipt_sha256=file_digest(Path(result['receipt']))[0])
        if (final['implementation_sha256'] != snapshots['reconstruction_audit.py']
                or final['windows_implementation_sha256'] != snapshots['windows.py']):
            raise ValueError('implementation changed during finalization')
        results.append(result)
        print(json.dumps(result), flush=True)
    summary = {'version': POLICY, 'references': results,
               'accepted_count': sum(r['accepted'] for r in results),
               'reference_count': len(results), 'implementation_sha256': snapshots,
               'native_power_unchanged': True, 'clock_period_s': 1e-8,
               'scope': 'Archived references only; not repaired reference construction or 450 finalists.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    return summary


def restore(source, destination, expected_sha256):
    """Restore exactly one retained waveform, checking both retention hashes."""
    receipt = json.loads(source.with_suffix('.vcd.retention.json').read_text())
    if receipt['encoding'] != 'zstd' or receipt['sha256'] != expected_sha256:
        raise ValueError('unexpected waveform receipt')
    packed = source.with_suffix('.vcd.zst')
    if file_digest(packed) != (receipt['retained_sha256'], receipt['retained_bytes']):
        raise ValueError('retained waveform hash/size mismatch')
    with destination.open('xb') as stream:
        subprocess.run(['zstd', '-qdc', str(packed)], stdout=stream, check=True)
    if file_digest(destination) != (expected_sha256, receipt['bytes']):
        raise ValueError('restored waveform hash/size mismatch')
    return receipt


PIN_TCL = '''
foreach name {_38591_/Y _38592_/Y} {
    set pin [get_pins $name]
    puts "AUDIT_PIN $name [get_property $pin activity] [get_property $pin slew_min_rise] [get_property $pin slew_min_fall] [get_property $pin slew_max_rise] [get_property $pin slew_max_fall]"
}
'''


def parse_report(text):
    if re.search(r'^Error:', text, re.M):
        raise ValueError('OpenSTA diagnostic error')
    leaves = {k: float(v) for k, v in re.findall(r'^AUDIT_LEAF (\S+) (\S+)$', text, re.M)}
    counts = {k: float(v) for k, v in re.findall(
        r'(\S+) transitions ([0-9.]+) activity ', text)}
    pins = re.findall(r'^AUDIT_PIN (.+)$', text, re.M)
    if not leaves or not counts or not pins:
        raise ValueError('incomplete diagnostic report')
    return {'leaves': leaves, 'counts': counts, 'pins': pins}


def compare(full, bins, durations):
    if (len(bins) != len(durations) or not bins
            or any(not math.isfinite(d) or d <= 0 for d in durations)):
        raise ValueError('positive duration per bin required')
    for field in ('leaves', 'counts'):
        if any(set(b[field]) != set(full[field]) for b in bins):
            raise ValueError(f'{field} coverage differs')
    mismatches = {pin: sum(b['counts'][pin] for b in bins) - count
                  for pin, count in full['counts'].items()
                  if sum(b['counts'][pin] for b in bins) != count}
    rows = []
    for cell, value in full['leaves'].items():
        weighted = sum(b['leaves'][cell] * d for b, d in zip(bins, durations)) / sum(durations)
        rows.append({'cell': cell, 'full_w': value, 'weighted_w': weighted,
                     'difference_w': weighted - value,
                     'bins_w': [b['leaves'][cell] for b in bins]})
    rows.sort(key=lambda r: abs(r['difference_w']), reverse=True)
    return {'counted_pins': len(full['counts']), 'count_mismatches': mismatches,
            'full_w': sum(full['leaves'].values()),
            'weighted_w': sum(row['weighted_w'] for row in rows),
            'largest_differences': rows[:50]}


def unclipped_switching(counts, durations_s, effective_densities, switching_w):
    """Diagnostic counterfactual for a single-output, fixed-load cell.

    Recover its fixed C*V^2/2 coefficient from measured effective density and
    switching, then apply counted VCD density. Never use this on multi-output
    cell totals. The returned estimate is separate from native OpenSTA power.
    """
    size = len(counts)
    if size < 2 or any(len(v) != size for v in
                       (durations_s, effective_densities, switching_w)):
        raise ValueError('matching full-plus-bin observations required')
    if any(not math.isfinite(x) or x < 0 for values in
           (counts, effective_densities, switching_w) for x in values):
        raise ValueError('invalid activity/power')
    if any(not math.isfinite(d) or d <= 0 for d in durations_s):
        raise ValueError('positive finite durations required')
    if not math.isclose(durations_s[0], sum(durations_s[1:]), rel_tol=1e-12):
        raise ValueError('bin durations do not reconstruct full duration')
    if counts[0] != sum(counts[1:]):
        raise ValueError('transition counts do not reconstruct')
    coefficients = [p / d for p, d in zip(switching_w, effective_densities) if d > 0]
    if not coefficients or any(p != 0 for p, d in zip(switching_w, effective_densities) if d == 0):
        raise ValueError('cannot identify switching coefficient')
    coefficient = sum(coefficients) / len(coefficients)
    # Tcl activity property has only six significant digits; this is a
    # diagnostic fit check, not a change to the evaluator acceptance threshold.
    if any(not math.isclose(c, coefficient, rel_tol=1e-5) for c in coefficients):
        raise ValueError('load/voltage coefficient differs across windows')
    raw = [n / d for n, d in zip(counts, durations_s)]
    if any(e > r * (1 + 1e-5) for e, r in zip(effective_densities, raw)):
        raise ValueError('effective activity exceeds counted activity')
    powers = [coefficient * d for d in raw]
    return {'coefficient_j_per_transition': coefficient, 'raw_density_hz': raw,
            'effective_density_hz': effective_densities, 'unclipped_switching_w': powers,
            'native_switching_w': switching_w,
            'clipped': [e < r * (1 - 1e-5) for e, r in zip(effective_densities, raw)]}


def minimal_reproducer(out, tool, liberty):
    """One loaded gate, explicit VCD activity, unchanged 10 ns clock."""
    out.mkdir(parents=True, exist_ok=False)
    netlist, waveform = out / 'mapped.v', out / 'activity.vcd'
    netlist.write_text('module repro(input clk, input a, output y);\n'
                       'sky130_fd_sc_hd__a31oi_1 gate0 (.A1(a), .A2(1\'b1), '
                       '.A3(1\'b1), .B1(1\'b0), .Y(y));\nendmodule\n')
    lines = ['$timescale 1ps $end', '$scope module repro $end',
             '$var wire 1 ! clk $end', '$var wire 1 " a $end',
             '$var wire 1 # y $end', '$scope module gate0 $end',
             '$var wire 1 # Y $end', '$var wire 1 " A1 $end',
             '$upscope $end', '$upscope $end', '$enddefinitions $end',
             '#0', '0!', '0"', '1#']
    a = clk = 0
    for tick in range(5000, 8000001, 5000):
        lines.extend([f'#{tick}', f'{1-clk}!'])
        clk = 1 - clk
        index = (tick - 1) // 1000000
        interval = 10000 if index in (3, 4) else 100000
        if tick % interval == 0:
            a = 1 - a
            lines.extend([f'{a}"', f'{1-a}#'])
    lines.extend(['#8001001', '0!'])
    waveform.write_text('\n'.join(lines) + '\n')
    prefix = (f'read_liberty {quoted(liberty)}\nread_verilog {quoted(netlist)}\n'
              'link_design repro\ncreate_clock -period 10 [get_ports clk]\n'
              'set_load 5 [get_ports y]\nsta::set_debug read_vcd 1\n')
    rows = []
    for name, begin, end in [('full', 1, 8000001),
                             *[(f'bin-{i}', i*1000000+1, (i+1)*1000000+1) for i in range(8)]]:
        tcl = out / f'{name}.tcl'
        tcl.write_text(prefix + f'read_vcd -scope repro -begin_time {begin} -end_time {end} {quoted(waveform)}\n'
                       'report_power -digits 12\n'
                       'puts "REPRO_POWER [sta::instance_power [get_cells gate0] [sta::cmd_scene]]"\n'
                       'puts "REPRO_ACTIVITY [get_property [get_pins gate0/Y] activity]"\n'
                       'puts "REPRO_SLEW [get_property [get_pins gate0/Y] slew_max_rise] [get_property [get_pins gate0/Y] slew_max_fall]"\n')
        result = subprocess.run([str(tool), '-no_init', '-exit', str(tcl)],
                                text=True, capture_output=True, check=True, timeout=30)
        text = result.stdout + result.stderr
        (out / f'{name}.rpt').write_text(text)
        if re.search(r'^Error:', text, re.M):
            raise ValueError('reproducer error')
        rows.append({'name': name, 'duration_s': (end-begin)*1e-12,
                     'count': float(re.search(r'gate0/Y transitions (\S+)', text)[1]),
                     'switching_w': float(re.search(r'^REPRO_POWER (.+)$', text, re.M)[1].split()[1]),
                     'effective_density_hz': float(re.search(r'^REPRO_ACTIVITY (\S+)', text, re.M)[1]),
                     'slew_ns': re.search(r'^REPRO_SLEW (.+)$', text, re.M)[1]})
    result = unclipped_switching(*[[r[key] for r in rows] for key in
                                  ('count', 'duration_s', 'effective_density_hz', 'switching_w')])
    result['observations'] = rows
    (out / 'reproducer.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def summarize_pin_audit(out, measurement):
    """Explain existing reports without replaying power or replacing evidence."""
    record = json.loads(measurement.read_text())['power']
    names = ['full', *[r['name'] for r in record['windows']]]
    reports = [parse_report((out / f'{name}.rpt').read_text()) for name in names]
    durations = [sum(record['grid']['durations_s']), *record['grid']['durations_s']]
    aggregate = compare(reports[0], reports[1:], durations[1:])
    if aggregate['count_mismatches']:
        raise ValueError('counting mismatch must be resolved before counterfactual')
    details = {}
    # These two mapped Ibex cells each have exactly one output, Y. This is
    # intentionally not a generic correction of arbitrary multi-output cells.
    for pin in ('_38591_/Y', '_38592_/Y'):
        cell = pin.split('/')[0]
        counts = [r['counts'][pin] for r in reports]
        fields = [next(p.split() for p in r['pins'] if p.split()[0] == pin)
                  for r in reports]
        effective = [float(p[1]) for p in fields]
        powers = [r['leaves'][cell] for r in reports]
        result = unclipped_switching(counts, durations, effective, powers)
        slews = [[float(v) for v in p[4:8]] for p in fields]
        if any(s != slews[0] for s in slews):
            raise ValueError('slew changes across windows')
        # Pinned single-corner setup: minimum of rise/fall averages across
        # the min/max delay analysis points, not minimum individual slew.
        min_average_slew_s = min(sum(slews[0][:2]), sum(slews[0][2:])) * .5e-9
        cap = 1 / min_average_slew_s if min_average_slew_s > 0 else None
        predicted = [min(r, cap) if cap is not None else r for r in result['raw_density_hz']]
        if any(not math.isclose(a, b, rel_tol=1e-5) for a, b in zip(predicted, effective)):
            raise ValueError('slew cap does not explain measured density')
        result.update(counts=counts, min_average_slew_s=min_average_slew_s,
                      density_cap_hz=cap, predicted_density_hz=predicted,
                      slew_min_rise_fall_max_rise_fall_ns=slews[0])
        details[pin] = result
    target = details['_38591_/Y']
    corrected = [sum(r['leaves'].values()) - target['native_switching_w'][i]
                 + target['unclipped_switching_w'][i] for i, r in enumerate(reports)]
    weighted = sum(p*d for p, d in zip(corrected[1:], durations[1:])) / durations[0]
    result = {'version': 'ibex-unclipped-switching-counterfactual-v1',
              'scope': 'Diagnostic only: raw VCD density times fixed C*V^2/2; native internal power unchanged.',
              'measurement_sha256': file_digest(measurement)[0],
              'clock_period_s': record['clock_period_s'],
              'counted_pins': aggregate['counted_pins'], 'count_mismatches': {},
              'pins': details, 'corrected_switching_w': corrected,
              'corrected_weighted_switching_w': weighted,
              'strict_reconstruction': reconstruction(corrected[0], weighted),
              'native_difference_w': aggregate['weighted_w'] - aggregate['full_w'],
              'other_cells_difference_w':
                  aggregate['weighted_w'] - aggregate['full_w']
                  - (sum(p*d for p, d in zip(target['native_switching_w'][1:], durations[1:]))
                     / durations[0] - target['native_switching_w'][0]),
              'artifacts': {f'{n}.{ext}': file_digest(out / f'{n}.{ext}')[0]
                            for n in names for ext in ('tcl', 'rpt')}}
    with (out / 'pin-analysis.json').open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurement', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--slew-policy', action='store_true',
                        help='Generate a new slew-verified-v1 production-policy receipt')
    parser.add_argument('--waveform', type=Path, help='Reuse an existing hash-verified restored VCD')
    parser.add_argument('--summarize-only', action='store_true',
                        help='Analyze saved diagnostic reports, without any power replay')
    args = parser.parse_args(argv)
    if args.slew_policy:
        print(json.dumps(audit_archived(args.measurement, args.out, waveform=args.waveform)))
        return
    record = json.loads(args.measurement.read_text())['power']
    if record['clock_period_s'] != 1e-8 or len(record['windows']) != 8:
        raise ValueError('this diagnostic requires the Ibex 10 ns eight-bin measurement')
    root = Path.cwd()
    tool = root / 'out/tools/opensta-a9a3f30/bin/sta'
    liberty = root / 'benchmarks/support/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib'
    source = args.measurement.parent / 'gls/power_gls.vcd'
    inputs = record['inputs']
    for path in (tool, root / 'out/ibex-matched-gls-dev-v1/synthesis-frozen-12-v3/mapped.v'):
        if file_digest(path)[0] != inputs[str(path)]:
            raise ValueError(f'input hash mismatch: {path}')
    lib_hash = next(v for k, v in inputs.items() if k.endswith('.lib'))
    if file_digest(liberty)[0] != lib_hash:
        raise ValueError('Liberty hash mismatch')
    if args.summarize_only:
        result = summarize_pin_audit(args.out, args.measurement)
        print(json.dumps(result['strict_reconstruction']), flush=True)
        return
    args.out.mkdir(parents=True, exist_ok=False)
    waveform = args.out / 'power_gls.vcd'
    receipt = restore(source, waveform, inputs[str(source.resolve())])
    (args.out / 'restore.json').write_text(json.dumps(receipt, indent=2) + '\n')

    def run(row):
        name = row['name']
        source_tcl = args.measurement.parent / 'power' / f'{name}.tcl'
        if file_digest(source_tcl)[0] != record['artifact_sha256'][f'{name}.tcl']:
            raise ValueError('source Tcl hash mismatch')
        text = source_tcl.read_text()
        text = text.replace('third_party/liberty/', 'benchmarks/support/liberty/')
        text = text.replace('{' + str(source.resolve()) + '}', quoted(waveform))
        text = text.replace('read_vcd ', 'sta::set_debug read_vcd 1\nread_vcd ')
        text = text.replace('report_power ', 'sta::set_debug read_vcd 0\nreport_power ')
        text = text.replace('    incr leaf_count',
                            '    puts "AUDIT_LEAF [get_full_name $inst] [format %.17g [lindex $values 1]]"\n    incr leaf_count')
        tcl, report = args.out / f'{name}.tcl', args.out / f'{name}.rpt'
        tcl.write_text(text + PIN_TCL)
        with report.open('x') as stream:
            subprocess.run([str(tool), '-no_init', '-exit', str(tcl)],
                           stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=180)
        result = parse_report(report.read_text())
        if len(result['leaves']) != row['leaf_count']:
            raise ValueError('leaf coverage differs from source')
        print(f'completed {name}', flush=True)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        full, *bins = executor.map(run, [record['full'], *record['windows']])
    result = compare(full, bins, record['grid']['durations_s'])
    result.update(version='ibex-reconstruction-audit-v1',
                  measurement=str(args.measurement.resolve()),
                  measurement_sha256=file_digest(args.measurement)[0],
                  clock_period_s=record['clock_period_s'],
                  pin_reports=[r['pins'] for r in [full, *bins]],
                  selected_counts={pin: [r['counts'][pin] for r in [full, *bins]]
                                   for pin in ('_38591_/Y', '_38592_/Y')})
    (args.out / 'audit.json').write_text(json.dumps(result, indent=2) + '\n')
    summary = summarize_pin_audit(args.out, args.measurement)
    print(json.dumps(summary['strict_reconstruction']), flush=True)


if __name__ == '__main__':
    main()
