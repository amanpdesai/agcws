"""Reference-scaled power tracking, without relabeling activity as watts."""

import math
from pathlib import Path

from agcws.evaluation.power.windows import reconstruction


def compare_measurements(candidate, reference):
    """Join measured evidence only when task, physical setup and windows agree."""
    a, b = candidate['activity'], reference['activity']
    if b.get('role') != 'power_reference':
        raise ValueError('reference must be a preselected power reference')
    for name in ('domain', 'target', 'target_rates', 'scale'):
        if a[name] != b[name]:
            raise ValueError(f'candidate/reference task differs: {name}')
    left, right = candidate['power'], reference['power']
    for name in ('scope', 'clock_period_s', 'tool_version'):
        if left[name] != right[name]:
            raise ValueError(f'candidate/reference power setup differs: {name}')
    def identity(power):
        inputs = power['inputs']
        mapped = [v for k, v in inputs.items() if Path(k).name == 'mapped.v']
        libraries = sorted(v for k, v in inputs.items() if Path(k).suffix == '.lib')
        if len(mapped) != 1 or not libraries:
            raise ValueError('power report lacks unique netlist and Liberty identity')
        return mapped, libraries
    if identity(left) != identity(right):
        raise ValueError('candidate/reference netlist or Liberty differs')
    durations = left['grid']['durations_s']
    if durations != right['grid']['durations_s']:
        raise ValueError('candidate/reference observation windows differ')
    for measurement in (candidate, reference):
        power = measurement['power']
        diagnostic = power.get('switching_reconstruction', {})
        if (diagnostic.get('policy') == 'slew-verified-v1'
                or measurement['activity'].get('reconstruction_policy') == 'slew-verified-v1'):
            try:
                values = [w['leaf_switching_sum_w'] for w in power['windows']]
                spans = power['grid']['durations_s']
                if len(values) != len(spans) or not spans or any(d <= 0 for d in spans):
                    raise ValueError('invalid proof windows')
                weighted = math.fsum(v*d for v, d in zip(values, spans))/math.fsum(spans)
                checked = reconstruction(power['full']['leaf_switching_sum_w'], weighted,
                    policy='slew-verified-v1',
                    top='ibex_top' if measurement['activity']['domain'] == 'ibex-temporal' else None,
                    period_s=power['clock_period_s'], proof=diagnostic.get('proof'),
                    window_values=values, durations_s=spans)
                hashes = diagnostic.get('proof', {}).get('report_sha256', {})
                names = [Path(p).name for p in hashes]
                artifacts_match = (len(set(names)) == len(values)+1
                                   and all(power['artifact_sha256'].get(Path(p).name) == h
                                           for p, h in hashes.items()))
                valid = (diagnostic.get('policy') == 'slew-verified-v1'
                         and checked['accepted_estimate']
                         and artifacts_match
                         and checked['pass'] == power['switching_additivity_pass']
                         and math.isclose(weighted, power['weighted_leaf_switching_w'],
                                          rel_tol=1e-12, abs_tol=1e-15))
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                valid = False
            if not valid:
                raise ValueError('power measurement lacks a matching verified slew proof')
        elif not power['switching_additivity_pass']:
            if not (measurement['activity']['domain'] == 'ibex-temporal'
                    and power['clock_period_s'] == 1e-8
                    and diagnostic.get('policy') == 'ibex-10ns-estimate-v1'
                    and diagnostic.get('accepted_estimate') is True):
                raise ValueError('power measurement failed switching additivity')
        if min(measurement['pin_annotation_fractions']) < .99:
            raise ValueError('power measurement lacks required annotation')
        if measurement['gate_dynamic_power_w'] != [w['dynamic_power_w'] for w in power['windows']]:
            raise ValueError('power vector differs from measured window reports')
    return {'candidate_case': candidate['case_id'], 'reference_case': reference['case_id'],
            'domain': a['domain'], 'target': a['target'], 'policy': a['policy'],
            'seed': a['seed'], 'activity_max_bin_error': a['max_bin_error'],
            'reference_activity_solved': b['activity_solved'],
            'candidate_switching_reconstruction': left.get('switching_reconstruction'),
            'reference_switching_reconstruction': right.get('switching_reconstruction'),
            'interpretation': ('qualified reference tracking' if b['activity_solved']
                               else 'descriptive reference only; requested activity target not matched'),
            **tracking(candidate['gate_dynamic_power_w'], reference['gate_dynamic_power_w'], durations)}


def main(argv=None):
    import argparse
    import json

    from agcws.core.provenance import file_sha256
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', type=Path, nargs='+', required=True)
    parser.add_argument('--references', type=Path, nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    references = {}
    for path in args.references:
        record = json.loads(path.read_text())
        key = record['activity']['domain'], record['activity']['target']
        if key in references:
            raise ValueError(f'duplicate power reference: {key}')
        references[key] = record
    rows, missing = [], []
    for path in args.candidates:
        record = json.loads(path.read_text())
        key = record['activity']['domain'], record['activity']['target']
        if key not in references:
            missing.append({'measurement': str(path), 'reason': 'reference power not measured'})
        else:
            rows.append(compare_measurements(record, references[key]))
    report = {'version': 'reference-power-tracking-v1', 'comparisons': rows, 'missing': missing,
              'inputs': {str(p): file_sha256(p) for p in args.candidates + args.references}}
    with args.out.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')


def tracking(candidate, reference, durations):
    """Compare eight aligned dynamic-power bins using one reference scale.

    Inputs are watts and seconds. Alignment and provenance must already have
    been verified by the replay pipeline. No power-space solve gate is implied.
    """
    if not (len(candidate) == len(reference) == len(durations) == 8):
        raise ValueError("power comparison requires eight matched bins")
    if any(not math.isfinite(v) or v < 0 for v in [*candidate, *reference]):
        raise ValueError("power must be finite and nonnegative")
    if any(not math.isfinite(v) or v <= 0 for v in durations):
        raise ValueError("window durations must be finite and positive")
    duration = math.fsum(durations)
    ref_energy = math.fsum(p * t for p, t in zip(reference, durations))
    scale = ref_energy / duration
    if scale <= 0:
        raise ValueError("reference mean dynamic power must be positive")
    residual = [(a - b) / scale for a, b in zip(candidate, reference)]
    energy = math.fsum(p * t for p, t in zip(candidate, durations))
    rms = math.sqrt(math.fsum(v * v for v in residual) / 8)
    constant = math.fsum(reference) / 8
    floor = math.sqrt(math.fsum(((v - constant) / scale) ** 2 for v in reference) / 8)
    return {
        "scale": "duration-weighted reference mean dynamic power",
        "scale_w": scale,
        "signed_normalized_error": residual,
        "nrmse": rms,
        "max_bin_error": max(abs(v) for v in residual),
        "candidate_mean_w": energy / duration,
        "reference_mean_w": scale,
        "candidate_peak_bin_w": max(candidate),
        "reference_peak_bin_w": max(reference),
        "candidate_energy_j": energy,
        "reference_energy_j": ref_energy,
        "reference_modulation_fraction": (max(reference) - min(reference)) / scale,
        "best_constant_power_w": constant,
        "best_constant_nrmse": floor,
        "error_over_constant_floor": rms / floor if floor > 0 else None,
        "constant_reference": floor == 0,
        "claim": "Matched reference-power tracking; no power-space success gate.",
    }


if __name__ == '__main__':
    main()
