"""Summarize the final, validated power inventory without rerunning experiments."""

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, median

from agcws.evidence import catalog
from agcws.evidence.power import load as load_power
from agcws.evidence.power import unpack_record
from agcws.reporting.power_reference import compare_measurements

ROOT = Path(__file__).resolve().parents[2]
DESIGNS = ('aes', 'dma', 'ibex', 'mesh', 'redmule')
ARMS = ('phase-random', 'phase-ga', 'phase-model', 'flash-lite-medium', 'strong-medium-64k')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def describe(rows):
    if not rows:
        return {'n':0}
    ratios = [r['error_over_constant_floor'] for r in rows if r['error_over_constant_floor'] is not None]
    return dict(n=len(rows),mean_nrmse=mean(r['nrmse'] for r in rows),
        median_nrmse=median(r['nrmse'] for r in rows),
        mean_max_bin_error=mean(r['max_bin_error'] for r in rows),
        better_than_constant=sum(r['nrmse']<r['best_constant_nrmse'] for r in rows),
        mean_constant_nrmse=mean(r['best_constant_nrmse'] for r in rows),
        mean_error_over_constant_floor=mean(ratios) if ratios else None,
        qualified_reference_comparisons=sum(r['reference_activity_solved'] for r in rows))


def sensitivity(designs):
    """Descriptive matched comparisons, excluding Ibex as a whole design."""
    pairs, selected = [], {}
    for design, result in designs.items():
        if design == 'ibex':
            continue
        arm = min(ARMS[:3], key=lambda a: result['matched_strong'][a]['comparator']['mean_nrmse'])
        selected[design] = arm
        pair = result['matched_strong'][arm]
        pairs.append(pair)
    n = sum(p['strong']['n'] for p in pairs)
    return dict(excluded_design='ibex', selected_comparators=selected, matched_pairs=n,
        mean_strong_nrmse=sum(p['strong']['mean_nrmse']*p['strong']['n'] for p in pairs)/n,
        mean_classical_nrmse=sum(p['comparator']['mean_nrmse']*p['comparator']['n'] for p in pairs)/n,
        lower_strong_mean_on_each_remaining_design=all(
            p['strong']['mean_nrmse'] < p['comparator']['mean_nrmse'] for p in pairs),
        scope='Descriptive pair-weighted means against the lowest-mean measured classical policy per design; no significance test.')


def analyze(output=None):
    from agcws.reporting.redmule_validation import verify as verify_redmule
    from agcws.reporting.references import verify as verify_references
    verify_references(ROOT)
    verify_redmule(ROOT)
    designs, inputs, examples = {}, {}, []
    for design in DESIGNS:
        buckets, _ = load_power(ROOT, design, inputs)
        references, candidates, coverage, failures, seen = {}, [], {}, [], set()
        for bucket in buckets:
            rows = bucket['records']
            coverage[bucket['bucket']] = {'planned':len(rows), 'measured':len(rows), 'failed':0}
            for row in rows:
                record = unpack_record(row)
                seen.add(tuple(row['case'][k] for k in ('policy','target','seed')))
                if row['case'].get('role') == 'power_reference':
                    references[row['case']['target']] = record
                else:
                    candidates.append(record)
        comparisons = [compare_measurements(c, references[c['activity']['target']]) for c in candidates]
        # Keep the already published Mesh illustration tasks and seed. These
        # power finalists follow the power selector, not the activity-figure
        # earliest-slot-only tie rule. Neither selector observes gate power.
        if design=='mesh':
            for target in ('confirmation-alternating','confirmation-irregular'):
                ref=references[target]
                chosen=[c for c in candidates if c['activity']['target']==target and c['activity']['seed']==9100]
                if {c['activity']['policy'] for c in chosen}!=set(ARMS):
                    raise ValueError('incomplete fixed power illustration')
                examples.append(dict(target=target,seed=9100,reference=ref,
                                     candidates={c['activity']['policy']:c for c in chosen}))
        if len(references)!=9 or any(sum(p==arm for p,t,s in seen)!=90 for arm in ARMS):
            raise ValueError('incomplete finalist inventory')
        nonflat = [r for r in comparisons if not r['target'].endswith('flat_control')]
        by_arm = {arm:describe([r for r in nonflat if r['policy']==arm]) for arm in ARMS}
        matched = {}
        for arm in ARMS[:-1]:
            other = {(r['target'],r['seed']):r for r in nonflat if r['policy']==arm}
            strong = [r for r in nonflat if r['policy']==ARMS[-1] and (r['target'],r['seed']) in other]
            matched[arm] = dict(strong=describe(strong),comparator=describe(list(other.values())),
                scope='Descriptive matched measured pairs; missing measurements excluded, no significance claim.')
        diagnostics = {}
        for target,record in references.items():
            r=compare_measurements(record,record)
            diagnostics[target] = {k:r[k] for k in ('reference_activity_solved','reference_mean_w',
                'reference_modulation_fraction','best_constant_nrmse','reference_switching_reconstruction')}
        designs[design] = dict(coverage=coverage,nonflat_by_arm=by_arm,matched_strong=matched,
            reconstruction_counts=dict(
                nonflat_candidates_strict=sum(c['power']['switching_additivity_pass'] for c in candidates if not c['activity']['target'].endswith('flat_control')),
                nonflat_candidates_slew_verified=sum(c['power'].get('switching_reconstruction', {}).get('policy')=='slew-verified-v1' for c in candidates if not c['activity']['target'].endswith('flat_control')),
                nonflat_references_strict=sum(c['power']['switching_additivity_pass'] for t,c in references.items() if not t.endswith('flat_control')),
                nonflat_references_slew_verified=sum(c['power'].get('switching_reconstruction', {}).get('policy')=='slew-verified-v1' for t,c in references.items() if not t.endswith('flat_control'))),
            exclusions_by_arm={arm:dict(total=sum(r['case']['policy']==arm for r in failures),
                nonflat=sum(r['case']['policy']==arm and not r['case']['target'].endswith('flat_control') for r in failures)) for arm in ARMS},
            qualified_reference_by_arm={arm:describe([r for r in nonflat if r['policy']==arm
                and r['reference_activity_solved']]) for arm in ARMS},
            references=diagnostics,comparisons=comparisons,failures=failures)
        print(design, by_arm[ARMS[-1]],flush=True)
    summary = dict(version=3,inputs=inputs,extractor_sha256=digest(Path(__file__).read_bytes()),designs=designs,
        excluding_ibex=sensitivity(designs),
        illustrations=examples,illustration_scope='Fixed published Mesh targets and seed. Power-finalist selector; references are descriptive, not requested power targets.',
        scope='Completed finalist power, controls separate, aligned reference-mean normalization. Validation evidence is retained with each design. No power-space solve gate or silicon-accuracy claim.')
    output = output or catalog.summary(ROOT, 'power')
    output.write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# Completed mapped-gate power assessment','',summary['scope'],'',
           '| Design | Random | GA | Phase-model | Flash-Lite | Gemini 3.8 |',
           '| --- | ---: | ---: | ---: | ---: | ---: |']
    for design,result in designs.items():
        values = result['nonflat_by_arm']
        lines.append('| '+design+' | '+' | '.join(f"{values[a]['mean_nrmse']:.5f} ({values[a]['n']})" for a in ARMS)+' |')
    strong_count=sum(v['coverage']['strong-'+d]['measured'] for d,v in designs.items())
    reference_count=sum(v['coverage']['references-'+d]['measured'] for d,v in designs.items())
    failed_count=sum(len(v['failures']) for v in designs.values())
    qualified_count=sum(r['reference_activity_solved'] for v in designs.values()
                        for t,r in v['references'].items() if not t.endswith('flat_control'))
    better_count=sum(v['nonflat_by_arm'][ARMS[-1]]['better_than_constant'] for v in designs.values())
    lines += ['', 'Entries are mean normalized RMS power error, with measured nonflat run count in parentheses. '
              'Normalization uses the duration-weighted mean of the fixed reference, not the activity span. '
              'Failed cases are absent, never replaced by zeros. `matched_strong` reports identical measured subsets for each comparator.', '',
              f'{strong_count}/450 strong and {reference_count}/45 reference replays completed. '
              f'{failed_count} measurements remain excluded. '
              + 'Measurements pass strict reconstruction or the per-case slew-clipping audit. Controls remain separate.', '',
              f'Of 40 nonflat reference workloads, {qualified_count} meet the activity gate. '
              'Other reference comparisons describe workloads, not validation of the requested target. '
              'Reference modulation and the best constant approximation (the eight-bin mean) are retained for every task. '
              f'{better_count}/400 strong nonflat measurements beat their reference\'s constant approximation.', '',
              'Reproduce with `.venv/bin/python paper/scripts/extract_power.py`. '
              'The five compressed archives contain the final measurements and validation receipts. '
              'Extraction checks the recorded evidence and comparison arithmetic without rerunning OpenSTA.', '']
    result = summary['excluding_ibex']
    lines += ['Excluding Ibex leaves '+str(result['matched_pairs'])+' measured pairs. '
              f"Mean NRMSE is {100*result['mean_strong_nrmse']:.3f}% for Gemini and "
              f"{100*result['mean_classical_nrmse']:.3f}% for the selected classical comparators. "
              'The comparison remains descriptive, not a power-space success rate.', '']
    output.with_suffix('.md').write_text('\n'.join(lines))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Alternative summary destination')
    args = parser.parse_args()
    analyze(args.out)


if __name__ == '__main__':
    main()
