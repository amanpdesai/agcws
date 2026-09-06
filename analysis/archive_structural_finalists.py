"""Reconcile declared finalists with completed, input-hashed gate replays."""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

from analysis.audit_structural_panel import require
from analysis.matched_power import parse_report
from analysis.select_structural_finalists import select
from analysis.vcd_window import window
from validation.aes_gls import sha


def build(selection_path, validation, heldout, runs):
    raw = selection_path.read_bytes()
    selected = json.loads(raw)
    require(selected == select(heldout), 'selection differs from independently reselected held-out finalists')
    require(len(selected['cases']) == 16, 'requires all sixteen declared cases')
    require(len({c['run'] for c in selected['cases']}) == 16, 'duplicate finalist cases')
    cases, unique = [], {}
    for case in selected['cases']:
        ident = case['replay_id']
        if ident is None:
            cases.append({**case, 'validation_status': 'no_valid_finalist'})
            continue
        case_path = validation / 'cases' / f"{case['design']}-{case['target']}-{case['policy']}.json"
        actual = json.loads(case_path.read_text())
        for key in ('run', 'replay_id', 'proposal_index', 'evaluation_index'):
            require(actual[key] == case[key], f'finalist selection mismatch: {key}')
        root = validation / 'replays' / ident
        completed = json.loads((root / 'completed.json').read_text())
        require(completed['replay'] == selected['unique_replays'][ident], 'replay contract mismatch')
        comparison_path = root / 'archive/comparison.json'
        require(sha(comparison_path) == completed['comparison_sha256'], 'comparison checksum mismatch')
        comparison = json.loads(comparison_path.read_text())
        for name, expected in comparison['artifact_sha256'].items():
            require(sha(root / 'archive' / name) == expected, f'validation artifact changed: {name}')
        measured_power = parse_report((root / 'archive/power.rpt').read_text())
        require(all(comparison[key] == value for key, value in measured_power.items()),
                'archived power components differ from raw report')
        require(comparison['clock_edges'] == case['activity_profile']['provenance']['clock_edges'],
                'selected measurement window mismatch')
        require(comparison['rtl']['window_rates'] == case['activity_profile']['windowed'],
                'selected activity profile mismatch')
        rtl_waveform = runs / case['run'] / 'evaluations' / f"trial-{case['evaluation_index']:05d}" / 'activity.vcd'
        gate_window = (unique[ident]['waveform_windows']['gls'] if ident in unique
                       else window(root / 'gls/activity.vcd'))
        spans = {'rtl': window(rtl_waveform), 'gls': gate_window}
        require(all(math.isclose(spans['rtl'][key], spans['gls'][key], rel_tol=0, abs_tol=1e-15)
                    for key in ('start_s', 'end_s', 'duration_s')), 'waveform spans differ')
        if ident not in unique:
            unique[ident] = {'completion': completed, 'comparison': comparison, 'waveform_windows': spans}
        cases.append({**case, 'validation_status': 'matched', 'cache_reused': actual['cache_reused'],
                      'rtl_waveform_window': spans['rtl']})
    require(set(unique) == set(selected['unique_replays']), 'missing or unexpected replay')
    return {'scope': 'Predeclared seed-400 descriptive validation, not a general proxy-power correlation.',
            'selection_sha256': hashlib.sha256(raw).hexdigest(),
            'selected_cases': len(cases), 'matched_cases': sum(c['validation_status'] == 'matched' for c in cases),
            'unique_replays': unique, 'cases': cases,
            'validation_wall_clock_s': sum(r['completion']['wall_clock_s'] for r in unique.values()),
            'cost_scope': 'Measured successful unique replay pipeline time; excludes search, synthesis and failed attempts.',
            'limitations': ['Full-window mean power does not validate an eight-bin power shape.',
                            'Zero-delay functional gates omit timing-induced glitches.',
                            'Duplicate finalists are not independent measurements.']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--validation', type=Path, required=True)
    parser.add_argument('--heldout', type=Path, required=True)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.selection, args.validation, args.heldout, args.runs)
    args.archive.mkdir(parents=True, exist_ok=False)
    shutil.copy2(args.selection, args.archive / 'selection.json')
    for ident in result['unique_replays']:
        source = args.validation / 'replays' / ident
        destination = args.archive / 'replays' / ident
        shutil.copytree(source / 'archive', destination)
        shutil.copy2(source / 'completed.json', destination / 'completed.json')
    (args.archive / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Validated {result['matched_cases']}/{result['selected_cases']} cases, {len(result['unique_replays'])} unique replays")


if __name__ == '__main__':
    main()
