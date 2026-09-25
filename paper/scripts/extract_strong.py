"""Recompute completed strong-panel results from hash-verified packed trials.

Offline only. This audit checks tasks, initializations, cached measurements,
slot accounting and metric arithmetic, not new simulations or provider bills.
"""

import gzip
import argparse
import itertools
import json
import math
import random
from pathlib import Path
from statistics import mean

from agcws.evidence import catalog, packs
from agcws.reporting.baselines import aggregate
from agcws.reporting.metrics import error, key, max_bin_error, summarize
from agcws.reporting.statistics.inference import holm_bonferroni, paired_permutation_pvalue

ROOT = Path(__file__).resolve().parents[2]
ARM = 'strong-medium-64k'
DESIGNS = ('aes', 'dma', 'ibex', 'mesh', 'redmule')
BASELINES = ('phase-random', 'phase-ga', 'phase-model')


def close(a, b):
    if not math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12):
        raise ValueError(f'metric mismatch: {a} != {b}')


def records(archive, predicate):
    inventory = packs.manifest(archive)
    selected = packs.read_selected(archive, [p for p in inventory['files'] if predicate(p)])
    return {p[:-3]: json.loads(gzip.decompress(raw)) for p, raw in selected.items()}


def audit(design, baseline, capture_legacy=False):
    archive = catalog.design(ROOT, design, 'gemini_3_8')
    data = records(archive, lambda p: p.endswith(('/trials.json.gz', '/proposals.json.gz',
        '/result.json.gz', '/complete.json.gz', '/identity.json.gz')) or
        p in ('manifest.json.gz', 'complete.json.gz', 'continuation.json.gz'))
    manifest = data['manifest.json']
    spec = manifest['spec']
    # Retained cells reference original cache entries that were deliberately not
    # copied by the continuation. Preserve those measurements in a separate,
    # explicit companion rather than modifying either run or skipping checks.
    legacy_path = archive / 'retained-cache.json.gz'
    if capture_legacy:
        original = Path(data['continuation.json']['source'])
        if packs.sha(original/'manifest.json') != packs.manifest(archive)['run_manifest_sha256']:
            raise ValueError('original manifest differs')
        missing = {f"cache/{t['cache_id']}/result.json" for p,rows in data.items()
                   if p.endswith('/trials.json') for t in rows if t['valid']
                   and f"cache/{t['cache_id']}/result.json" not in data}
        companion = {p: {'sha256':packs.sha(original/p),'record':json.loads((original/p).read_text())}
                     for p in sorted(missing)}
        with legacy_path.open('xb') as stream:
            stream.write(gzip.compress(json.dumps(companion,sort_keys=True).encode(),mtime=0))
    legacy = json.loads(gzip.decompress(legacy_path.read_bytes()))
    data.update({p:r['record'] for p,r in legacy.items()})
    for field in set(spec) | set(baseline['spec']):
        if field not in ('name', 'policies', 'cost_ceiling_usd') and spec.get(field) != baseline['spec'].get(field):
            raise ValueError(f'{design}: unmatched task field {field}')
    if spec['policies'] != [ARM] or spec['success_metric'] != 'max-bin' or spec['tolerance'] != .05:
        raise ValueError('unexpected policy or acceptance rule')
    initial = records(catalog.design(ROOT, design, 'baselines'),
                      lambda p: '/batches/001/trials.json.gz' in p)
    cells = []
    manifest_sha = packs.manifest(archive)['run_manifest_sha256']
    if data['continuation.json']['manifest_sha256'] != manifest_sha:
        raise ValueError('continuation changed scientific manifest')
    expected = set()
    for target, seed in itertools.product(spec['targets'], spec['seeds']):
        prefix = f'panel/{target}/{seed}/{ARM}'
        expected.add(prefix + '/complete.json')
        identity = dict(target=target, seed=seed, arm=ARM, manifest_sha256=manifest_sha)
        if data[prefix + '/identity.json'] != identity:
            raise ValueError('cell identity mismatch')
        history = []
        for path in sorted(p for p in data if p.startswith(prefix + '/batches/') and p.endswith('/trials.json')):
            if any(t['valid'] and t['max_bin_error'] <= .05 for t in history):
                raise ValueError('continued after successful batch')
            trials = data[path]
            proposals = data[path.replace('/trials.json', '/proposals.json')]
            if len(trials) != spec['batch_size'] or len(proposals) != len(trials):
                raise ValueError('batch accounting mismatch')
            for proposal, trial in zip(proposals, trials, strict=True):
                if (any(trial.get(k) != v for k, v in proposal.items()) or trial.get('api_error')
                        or trial.get('stage') in ('API', 'PROVIDER')):
                    raise ValueError('trial/proposal mismatch or charged provider error')
                if trial['valid']:
                    close(trial['loss'], error(trial['rates'], spec['targets'][target], spec['scale']))
                    close(trial['max_bin_error'], max_bin_error(trial['rates'], spec['targets'][target], spec['scale']))
                    residual = [(a-b)/spec['scale'] for a,b in zip(trial['rates'],spec['targets'][target],strict=True)]
                    if residual != trial['residual']:
                        raise ValueError('signed residual mismatch')
                    cache_id = key({'program':trial['canonical_program'], 'measurement':manifest['measurement_fingerprint']})
                    cached = data[f'cache/{cache_id}/result.json']
                    if cache_id != trial['cache_id'] or not cached['valid'] or cached['profile']['window_rates'] != trial['rates']:
                        raise ValueError('cached activity mismatch')
                elif trial['loss'] is not None or trial.get('max_bin_error') is not None:
                    raise ValueError('invalid trial scored')
            history.extend(trials)
        for other in BASELINES:
            first = initial[f'panel/{target}/{seed}/{other}/batches/001/trials.json']
            for a,b in zip(history[:2],first,strict=True):
                if any(a.get(k) != b.get(k) for k in ('program','valid','rates','loss','max_bin_error')):
                    raise ValueError('shared initialization differs')
        summary = summarize(history,spec['budget'],spec['tolerance'],stop_on_success=True,success_metric='max-bin')
        stored = data[prefix + '/complete.json']
        if any(stored.get(k) != v for k,v in summary.items()) or stored['cell'] != identity:
            raise ValueError('saved completion does not match recomputed trajectory')
        cells.append({**summary,'target':target,'seed':seed,'arm':ARM,'internal_surrogate_candidates':0})
    actual = {p for p in data if p.startswith('panel/') and p.endswith('/complete.json')}
    if actual != expected or data['complete.json']['cells'] != len(cells):
        raise ValueError('missing/extra completed runs')
    groups = {name: aggregate([c for c in cells if c['target'].endswith('flat_control') == control])
              for name,control in [('nonflat',False),('control',True)]}
    return dict(manifest_sha256=manifest_sha, models=manifest['models'], cells=cells,
                **groups, archive=catalog.recorded(ROOT, archive),
                retained_cache_sha256=packs.sha(legacy_path),
                archive_manifest_sha256=packs.sha(archive/packs.PACK))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-legacy', action='store_true',
                        help='One-time exact original-cache companion capture; refuses overwrite')
    args = parser.parse_args()
    baseline_path = catalog.summary(ROOT, 'baselines')
    baseline = json.loads(baseline_path.read_text())
    designs, inference = {}, []
    for design in DESIGNS:
        result = audit(design,baseline['designs'][design],args.capture_legacy)
        designs[design] = result
        for arm in BASELINES:
            paired = []
            for seed in sorted({c['seed'] for c in result['cells']}):
                groups = ([c['auc'] for c in source if c['seed']==seed and c['arm']==policy
                           and not c['target'].endswith('flat_control')]
                          for source,policy in ((result['cells'],ARM),(baseline['designs'][design]['cells'],arm)))
                a,b = groups
                if len(a)!=8 or len(b)!=8:
                    raise ValueError('incomplete seed block')
                paired.append((mean(a),mean(b)))
            delta = [a-b for a,b in paired]
            rng = random.Random(9200)
            boots = sorted(mean(rng.choices(delta,k=len(delta))) for _ in range(10000))
            inference.append(dict(design=design,left=ARM,right=arm,seed_mean_differences=delta,
                mean_auc_difference=mean(delta),bootstrap_95_percent_ci=[boots[249],boots[9749]],
                exact_sign_flip_p=paired_permutation_pvalue([a for a,b in paired],[b for a,b in paired])))
        print(design, result['nonflat'],flush=True)
    adjusted = holm_bonferroni([r['exact_sign_flip_p'] for r in inference])
    for row,p in zip(inference,adjusted,strict=True):
        row['holm_adjusted_p'] = p
    output = catalog.summary(ROOT, 'gemini_3_8').parent
    output.mkdir(exist_ok=True)
    summary = dict(designs=designs,inference=inference,baseline_summary_sha256=packs.sha(baseline_path),
        extractor_sha256=packs.sha(Path(__file__)),
        inference_scope='Post-completion analysis: one Holm family of 15 strong-vs-classical contrasts; seed units on the fixed observed bank. Flash inference unchanged.',
        audit_scope='Hash-verified packed trials, matched tasks and initializations, cached activity, residuals, strict success, stopping and AUC. No independent simulation, provider-payload replay or reconciled billing claim.')
    catalog.summary(ROOT, 'gemini_3_8').write_text(json.dumps(summary,indent=2)+'\n')
    lines = ['# Completed strong-model comparison', '',
        'Gemini 3.8 Flash, MEDIUM reasoning, 65,536 output-token ceiling. All 450 designated continuation runs completed. No new model calls.', '',
        '| Design | Nonflat solves / 80 | Mean RMS-error AUC | Control solves / 10 |',
        '| --- | ---: | ---: | ---: |']
    for design,result in designs.items():
        lines.append(f"| {design} | {result['nonflat']['solved']} | {result['nonflat']['mean_auc']:.4f} | {result['control']['solved']} |")
    lines += ['', summary['audit_scope'], '', summary['inference_scope'], '',
        'Reproduce with `.venv/bin/python paper/scripts/extract_strong.py`. The results index locates each design archive and its retained-cache companion.', '',
        'Accounting includes recorded liabilities, not independently reconciled bills. Power results are in `power.json`.', '']
    (output/'gemini_3_8.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
