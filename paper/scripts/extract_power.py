"""Freeze and summarize completed, aligned finalist power measurements offline.

Capture reads completion receipts, checks measurement hashes and frozen
selection identity, and preserves all failed attempts. Re-analysis needs only
the compact per-design archives, not local waveforms or a new tool run.
"""

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from agcws.evidence import catalog
from agcws.reporting.metrics import key
from agcws.reporting.power_reference import compare_measurements

ROOT = Path(__file__).resolve().parents[2]
DESIGNS = ('aes', 'dma', 'ibex', 'mesh', 'redmule')
ARMS = ('phase-random', 'phase-ga', 'phase-model', 'flash-lite-medium', 'strong-medium-64k')
REVISION = ROOT / 'results/power-revision-v2.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(collections):
    entries = []
    for path in collections:
        entries.extend(json.loads(path.read_text()))
    grouped = defaultdict(list)
    for entry in entries:
        design = entry['name'].split('-')[-1]
        plan_raw = (ROOT / entry['plan']).read_bytes()
        plan = json.loads(plan_raw)
        if plan['sha256'] != key({k:v for k,v in plan.items() if k != 'sha256'}):
            raise ValueError('selection plan hash mismatch')
        directory = ROOT / entry['out']
        identity = json.loads((directory/'collection.json').read_text())
        if identity['plan_sha256'] != plan['sha256']:
            raise ValueError('collection selected a different plan')
        records = []
        for case in plan['cases']:
            cell = directory / case['id']
            failures = [{ 'path':str(p.relative_to(ROOT)), 'sha256':digest(p.read_bytes()),
                          'failure':json.loads(p.read_text())}
                        for p in sorted(cell.glob('attempt-*/failure.json'))]
            receipt = cell/'complete.json'
            row = dict(case=case, failures=failures)
            if receipt.exists():
                done = json.loads(receipt.read_text())
                path = cell / done['attempt'] / 'measurement.json'
                if path.resolve().parent.parent != cell.resolve():
                    raise ValueError('measurement path escaped case')
                raw = path.read_bytes()
                if digest(raw) != done['measurement_sha256']:
                    raise ValueError('completed measurement hash mismatch')
                measurement = json.loads(raw)
                if (measurement['case_id'] != case['id'] or measurement['activity'] != case
                        or measurement['plan_sha256'] != plan['sha256']):
                    raise ValueError('measurement differs from frozen finalist')
                row.update(status='measured',source=str(path.relative_to(ROOT)),receipt=done,
                           raw_measurement=raw.decode())
            elif failures:
                row['status'] = 'failed'
            else:
                raise ValueError(f'unfinished power case: {cell}')
            records.append(row)
        grouped[design].append(dict(bucket=entry['name'],plan_sha256=plan['sha256'],
            plan_file_sha256=digest(plan_raw),plan_path=str(Path(entry['plan']).relative_to(ROOT)
                if Path(entry['plan']).is_absolute() else entry['plan']),
            collection=identity,omitted=plan['omitted'],records=records))
    for design in DESIGNS:
        destination = catalog.design(ROOT, design, 'power')
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            raw=''.join(json.dumps(b,sort_keys=True)+'\n' for b in grouped[design]).encode()
            stream.write(gzip.compress(raw,mtime=0))


def unpack_record(row):
    raw = row['raw_measurement'].encode()
    if digest(raw) != row['receipt']['measurement_sha256']:
        raise ValueError('archived measurement hash mismatch')
    result = json.loads(raw)
    if result['activity'] != row['case'] or result['case_id'] != row['case']['id']:
        raise ValueError('archived selection mismatch')
    return result


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


def checked_bytes(entry, inputs):
    path = catalog.safe_path(ROOT, entry['path'])
    raw = path.read_bytes()
    if digest(raw) != entry['sha256']:
        raise ValueError(f'power revision input hash mismatch: {path}')
    inputs[entry['path']] = entry['sha256']
    return raw


def checked_json(entry, inputs):
    return json.loads(checked_bytes(entry, inputs))


def load_revision(path, inputs):
    if path is None:
        return None
    raw = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = digest(raw)
    revision = json.loads(raw)
    if revision['version'] not in ('power-revision-v1', 'power-revision-v2') or set(revision['designs']) != set(DESIGNS):
        raise ValueError('incomplete or unsupported power revision')
    return revision


def prepare_revision():
    """Freeze dependency hashes only after both reference and candidate checks finish."""
    from agcws.reporting.reference_repair import verify
    if verify(ROOT)['verified_native_measurements'] != 40:
        raise ValueError('reference bank is incomplete')
    inputs, designs = {}, {}
    for design in DESIGNS:
        name = f'results/{design}/power/repaired-references-v1/index.json'
        path = catalog.safe_path(ROOT, name)
        designs[design] = {'references': {'path': name, 'sha256': digest(path.read_bytes())}}
    name = 'results/ibex/power/slew-validation-v1/index.json'
    entry = {'path': name, 'sha256': digest(catalog.safe_path(ROOT, name).read_bytes())}
    audit = checked_json(entry, inputs)
    if not audit['all_passed'] or len(audit['entries']) != audit['expected_revisions']:
        raise ValueError('cannot freeze an unfinished candidate audit')
    designs['ibex']['candidates'] = entry
    from agcws.reporting.redmule_recovery import verify as verify_recovery
    if len(verify_recovery(ROOT)) != 22:
        raise ValueError('RedMulE recovery is incomplete')
    name = 'results/redmule/power/slew-recovery-v1/index.json'
    designs['redmule']['recovered'] = {'path': name, 'sha256': digest((ROOT / name).read_bytes())}
    record = {'version': 'power-revision-v2', 'designs': designs,
        'scope': 'Activity-qualified references and native candidate power with verified Ibex and RedMulE clipping. Search results and native power values unchanged.'}
    raw = json.dumps(record, indent=2)+'\n'
    if REVISION.exists() and REVISION.read_text() != raw:
        raise ValueError('published revision changed; create a new version')
    REVISION.write_text(raw)


def revised_candidate(record, entry, inputs):
    """Attach validation without silently changing the workload or native power."""
    replacement = checked_json(entry, inputs)
    if entry['original_sha256'] != record['_archive_sha256']:
        raise ValueError('candidate revision does not bind original measurement')
    for field in ('case_id', 'activity', 'plan_sha256', 'gate_dynamic_power_w',
                  'pin_annotation_fractions'):
        if replacement[field] != record[field]:
            raise ValueError(f'candidate revision changes frozen {field}')
    for field in ('scope', 'clock_period_s', 'tool_version', 'grid', 'full', 'windows',
                  'weighted_leaf_switching_w', 'switching_additivity_pass', 'inputs'):
        if replacement['power'][field] != record['power'][field]:
            raise ValueError(f'candidate revision changes native power {field}')
    if replacement['power']['switching_reconstruction'].get('policy') != 'slew-verified-v1':
        raise ValueError('candidate revision lacks slew validation')
    # compare_measurements validates the proof against native values and hashes.
    return replacement


def apply_revision(design, revision, references, candidates, inputs):
    refs = checked_json(revision['designs'][design]['references'], inputs)
    for name, sha in refs.get('inputs', {}).items():
        checked_bytes({'path': name, 'sha256': sha}, inputs)
    targets = {t for t in references if not t.endswith('flat_control')}
    if set(refs['references']) != targets or len(targets) != 8:
        raise ValueError('reference revision must cover all eight nonflat targets')
    for target, entry in refs['references'].items():
        new = checked_json(entry, inputs)
        old = references[target]
        for field in ('domain', 'target', 'target_rates', 'scale'):
            if new['activity'][field] != old['activity'][field]:
                raise ValueError(f'revised reference changes task {field}')
        if not new['activity']['activity_solved'] or new['activity']['max_bin_error'] > .05:
            raise ValueError('revised reference does not meet frozen activity gate')
        # Reuse the same setup/window checks as candidate/reference joins.
        compare_measurements(new, old, allow_legacy_estimate=True)
        references[target] = new
    entries = {}
    if 'candidates' in revision['designs'][design]:
        index = checked_json(revision['designs'][design]['candidates'], inputs)
        if not index.get('all_passed') or not index.get('complete'):
            raise ValueError('Ibex candidate audit incomplete or failed')
        for name, sha in index.get('inputs', {}).items():
            checked_bytes({'path': name, 'sha256': sha}, inputs)
        entries = dict(index['entries'])
    updated = []
    for record in candidates:
        if record['case_id'] in entries:
            record = revised_candidate(record, entries.pop(record['case_id']), inputs)
        if design == 'ibex' and not record['activity']['target'].endswith('flat_control'):
            p = record['power']
            if not p['switching_additivity_pass'] and p['switching_reconstruction'].get('policy') != 'slew-verified-v1':
                raise ValueError(f'Ibex candidate audit incomplete: {record["case_id"]}')
        record.pop('_archive_sha256', None)
        updated.append(record)
    if entries:
        raise ValueError('candidate revision contains unknown cases')
    return references, updated


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


def analyze(revision_path=REVISION, output=None):
    designs, inputs, examples = {}, {}, []
    revision = load_revision(revision_path, inputs)
    for design in DESIGNS:
        path = catalog.design(ROOT, design, 'power')
        inputs[catalog.recorded(ROOT, path)] = digest(path.read_bytes())
        buckets = [json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]
        references, candidates, coverage, failures, seen = {}, [], {}, [], set()
        recoveries, recovered_failures = {}, []
        if revision and 'recovered' in revision['designs'][design]:
            from agcws.reporting.redmule_recovery import verify as verify_recovery
            index = checked_json(revision['designs'][design]['recovered'], inputs)
            for name, sha in index['inputs'].items():
                checked_bytes({'path': name, 'sha256': sha}, inputs)
            recoveries = verify_recovery(ROOT)
            for entry in index['entries'].values():
                checked_bytes(entry, inputs)
        for bucket in buckets:
            rows = bucket['records']
            coverage[bucket['bucket']] = {'planned':len(rows),'measured':sum(r['status']=='measured' for r in rows),
                                          'failed':sum(r['status']=='failed' for r in rows)}
            for row in rows:
                label=(row['case']['policy'],row['case']['target'],row['case']['seed'])
                if label in seen:
                    raise ValueError('duplicate power case')
                seen.add(label)
                if row['status']=='failed':
                    case_id = row['case']['id']
                    if case_id not in recoveries:
                        failures.append(row)
                        continue
                    record = recoveries.pop(case_id)
                    recovered_failures.append(row)
                    coverage[bucket['bucket']]['measured'] += 1
                    coverage[bucket['bucket']]['failed'] -= 1
                    coverage[bucket['bucket']]['recovered'] = coverage[bucket['bucket']].get('recovered', 0) + 1
                else:
                    record = unpack_record(row)
                if record['plan_sha256'] != bucket['plan_sha256']:
                    raise ValueError('archived plan mismatch')
                if row['case'].get('role') == 'power_reference':
                    target = row['case']['target']
                    if target in references:
                        raise ValueError('duplicate reference')
                    references[target] = record
                else:
                    if row['status'] == 'measured':
                        record['_archive_sha256'] = row['receipt']['measurement_sha256']
                    candidates.append(record)
        if recoveries:
            raise ValueError('unused or unknown recovered cases')
        if revision:
            references, candidates = apply_revision(design, revision, references, candidates, inputs)
        else:
            for candidate in candidates:
                candidate.pop('_archive_sha256', None)
        comparisons = [compare_measurements(c,references[c['activity']['target']],
                                            allow_legacy_estimate=revision is None) for c in candidates]
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
            r=compare_measurements(record,record,allow_legacy_estimate=revision is None)
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
            references=diagnostics,comparisons=comparisons,failures=failures,
            recovered_failures=recovered_failures)
        print(design, by_arm[ARMS[-1]],flush=True)
    summary = dict(version=2 if revision else 1,inputs=inputs,extractor_sha256=digest(Path(__file__).read_bytes()),designs=designs,
        power_revision=revision['version'] if revision else None,
        excluding_ibex=sensitivity(designs),
        illustrations=examples,illustration_scope='Fixed published Mesh targets and seed. Power-finalist selector; references are descriptive, not requested power targets.',
        scope='Completed finalist power, controls separate, aligned reference-mean normalization. Original failures and verified recoveries retained. No power-space solve gate or silicon-accuracy claim.')
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
              f'{failed_count} measurements remain excluded. Original failures and verified recoveries are retained separately. '
              + ('Ibex and recovered RedMulE measurements pass strict reconstruction or the per-case slew-clipping audit. '
               'Original control measurements remain separate.' if revision else
               'Ibex uses the original estimate policy.'), '',
              f'Of 40 nonflat reference workloads, {qualified_count} meet the activity gate. '
              'Other reference comparisons describe workloads, not validation of the requested target. '
              'Reference modulation and the best constant approximation (the eight-bin mean) are retained for every task. '
              f'{better_count}/400 strong nonflat measurements beat their reference\'s constant approximation.', '',
              'Reproduce with `.venv/bin/python paper/scripts/extract_power.py`. `--capture` is the one-time local collection capture '
              'and refuses archive overwrite. The five compressed archives preserve full measurement JSON, '
              'receipt hashes, selection cases, collection identities, and failed attempts. '
              'This verifies recorded measurements and comparison arithmetic, not an independent OpenSTA rerun.', '']
    if revision:
        s = summary['excluding_ibex']
        lines += ['Excluding Ibex leaves '+str(s['matched_pairs'])+' measured pairs. '
                  f"Mean NRMSE is {100*s['mean_strong_nrmse']:.3f}% for Gemini and "
                  f"{100*s['mean_classical_nrmse']:.3f}% for the selected classical comparators. "
                  'The comparison remains descriptive, not a power-space success rate.', '']
    output.with_suffix('.md').write_text('\n'.join(lines))
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',action='store_true')
    parser.add_argument('--collections', type=Path, action='append',
                        help='Explicit collection index for a new capture; repeat as needed')
    parser.add_argument('--original-references', action='store_true',
                        help='Reproduce the original power comparison, without revision overlays')
    parser.add_argument('--out', type=Path, help='Alternative summary destination')
    parser.add_argument('--prepare-revision', action='store_true',
                        help='Freeze the complete repaired-reference and candidate-audit indexes')
    args=parser.parse_args()
    if args.capture:
        if not args.collections:
            parser.error('--capture requires explicit --collections files')
        capture(args.collections)
    if args.original_references and not args.out:
        parser.error('--original-references requires --out to preserve the current summary')
    if args.prepare_revision:
        if args.original_references:
            parser.error('--prepare-revision cannot use original references')
        prepare_revision()
    analyze(None if args.original_references else REVISION, args.out)


if __name__=='__main__':
    main()
