"""Audit completed CPU cells and produce reproducible descriptive aggregates."""

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from agcws.designs.temporal_registry import backend
from agcws.reporting.metrics import error, key, max_bin_error, summarize
from agcws.reporting.statistics.inference import holm_bonferroni, paired_permutation_pvalue

ARMS = ('phase-random', 'phase-ga', 'phase-model')
DESIGNS = ('aes', 'dma', 'ibex', 'mesh', 'redmule')


def read(path):
    return json.loads(path.read_text())


def close(a, b):
    if not math.isfinite(a) or not math.isfinite(b) or not math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f'numeric mismatch: {a} != {b}')


def audit(root):
    manifest = read(root/'manifest.json')
    spec = manifest['spec']
    if (spec['policies'] != list(ARMS) or spec['success_metric'] != 'max-bin'
            or spec['tolerance'] != .05 or spec['budget'] != 128 or spec['batch_size'] != 2
            or not spec['stop_on_success'] or manifest['models']):
        raise ValueError('unexpected frozen protocol')
    if list(root.glob('failure-*.json')) or list(root.glob('panel/**/request_started.json')):
        raise ValueError('failure or paid request in CPU panel')
    design = backend(spec['domain'])
    cells, unique_measurements = [], {}
    paths = set()
    for target, seed, arm in itertools.product(spec['targets'], spec['seeds'], ARMS):
        cell = root/'panel'/target/str(seed)/arm
        paths.add(cell/'complete.json')
        history, internal_candidates = [], 0
        stages = Counter()
        rng = random.Random(seed)
        for batch in sorted((cell/'batches').iterdir()):
            if any(t['valid'] and t['max_bin_error'] <= .05 for t in history):
                raise ValueError('continued after a successful batch')
            proposals, trials = read(batch/'proposals.json'), read(batch/'trials.json')
            n = min(2, 128-len(history))
            if len(proposals) != n or len(trials) != n:
                raise ValueError('proposal-slot accounting mismatch')
            prior = {t['slot']: t for t in history}
            for proposal, trial in zip(proposals, trials, strict=True):
                if any(trial.get(k) != v for k, v in proposal.items()) or not proposal['selected']:
                    raise ValueError('proposal/trial mismatch or unexpected filtering')
                if trial['slot'] != len(history)+trials.index(trial)+1:
                    raise ValueError('noncontiguous proposal index')
                if any(p not in prior or not prior[p]['valid'] for p in proposal['parents']):
                    raise ValueError('invalid or future parent')
                if not history:
                    if proposal['program'] != design.random(rng):
                        raise ValueError('seed-only initialization differs')
                elif arm != 'phase-model':
                    program, parents = design.propose_classical(arm, rng, trial['slot'], history)
                    if proposal['program'] != program or proposal['parents'] != parents:
                        raise ValueError('classical deterministic replay differs')
                else:
                    note = read(batch/f'model-decision-{trial["slot"]}.json')
                    if note['training_slots'] != [t['slot'] for t in history if t['valid']]:
                        raise ValueError('surrogate training uses different history')
                    if note['extra_simulations'] != 0:
                        raise ValueError('extra surrogate simulation')
                    if note.get('selected_sha256', key(proposal['program'])) != key(proposal['program']):
                        raise ValueError('surrogate selected program differs')
                    internal_candidates += note['internal_surrogate_candidates']
                if trial['valid']:
                    close(trial['loss'], error(trial['rates'], spec['targets'][target], spec['scale']))
                    close(trial['max_bin_error'], max_bin_error(trial['rates'], spec['targets'][target], spec['scale']))
                    expected_residual = [(a-b)/spec['scale'] for a, b in
                                         zip(trial['rates'], spec['targets'][target], strict=True)]
                    if expected_residual != trial['residual']:
                        raise ValueError('signed residual mismatch')
                else:
                    if trial['loss'] is not None or trial['max_bin_error'] is not None:
                        raise ValueError('invalid workload scored')
                    stages[trial['stage']] += 1
                if trial.get('cache_id'):
                    cached = read(root/'cache'/trial['cache_id']/'result.json')
                    canonical = trial.get('canonical_program')
                    if canonical is None:
                        canonical = design.canonical(trial['program'])
                    if key({'program': canonical, 'measurement': manifest['measurement_fingerprint']}) != trial['cache_id']:
                        raise ValueError('cache identity mismatch')
                    if cached['valid'] != trial['valid']:
                        raise ValueError('cached validity mismatch')
                    if trial['valid'] and cached['profile']['window_rates'] != trial['rates']:
                        raise ValueError('cached rates mismatch')
                    unique_measurements[trial['cache_id']] = cached.get('evaluation_s', 0)
            history.extend(trials)
        computed = summarize(history, 128, .05, stop_on_success=True, success_metric='max-bin')
        saved = read(cell/'complete.json')
        if any(saved[k] != v for k, v in computed.items()):
            raise ValueError('cell summary does not reproduce')
        if saved['cell']['target'] != target or saved['cell']['seed'] != seed or saved['cell']['arm'] != arm:
            raise ValueError('cell identity mismatch')
        cells.append({**computed, 'target': target, 'seed': seed, 'arm': arm,
                      'invalid_stages': dict(stages), 'internal_surrogate_candidates': internal_candidates})
    if paths != set(root.glob('panel/*/*/*/complete.json')):
        raise ValueError('missing or extra cells')
    complete = read(root/'complete.json')
    if complete['cells'] != len(cells) or complete['slots'] != sum(c['charged_slots'] for c in cells):
        raise ValueError('panel totals mismatch')
    if complete['liability_usd'] != 0:
        raise ValueError('nonzero model liability')
    for cell in complete['summaries']:
        ident = cell['cell']
        if cell != read(root/'panel'/ident['target']/str(ident['seed'])/ident['arm']/'complete.json'):
            raise ValueError('panel/cell summary mismatch')
    return {'manifest_sha256': hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest(),
            'spec': spec, 'cells': cells, 'unique_measurements': len(unique_measurements),
            'summed_unique_evaluation_wall_seconds': sum(unique_measurements.values()),
            'model_liability_usd': 0,
            'audit_scope': 'all metrics, cache identity/rates, initializations, random/GA replay, model history/selection records; not waveform resimulation or full ridge-fit replay'}


def aggregate(cells):
    return {'cells': len(cells), 'mean_auc': mean(c['auc'] for c in cells),
            'solved': sum(c['solved'] for c in cells),
            'mean_evaluations_to_target_censored': mean(c['evaluations_to_target'] for c in cells),
            'charged_slots': sum(c['charged_slots'] for c in cells),
            'valid_slots': sum(c['valid_slots'] for c in cells),
            'mean_best_max_bin_error': mean(c['best_max_bin_error'] for c in cells),
            'internal_surrogate_candidates': sum(c['internal_surrogate_candidates'] for c in cells)}


def infer(cells):
    by_seed = defaultdict(dict)
    for arm in ARMS:
        for seed in sorted({c['seed'] for c in cells}):
            by_seed[arm][seed] = mean(c['auc'] for c in cells if c['arm'] == arm and c['seed'] == seed)
    rows = []
    for left, right in itertools.combinations(ARMS, 2):
        a, b = list(by_seed[left].values()), list(by_seed[right].values())
        delta = [x-y for x, y in zip(a, b, strict=True)]
        rng = random.Random(20260917)
        boots = sorted(mean(rng.choices(delta, k=len(delta))) for _ in range(10000))
        rows.append({'left': left, 'right': right, 'seed_mean_differences': delta,
                     'mean_auc_difference': mean(delta), 'bootstrap_95_percent_ci': [boots[249], boots[9749]],
                     'exact_sign_flip_p': paired_permutation_pvalue(a, b)})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--design', choices=DESIGNS)
    args = parser.parse_args(argv)
    if args.design:
        result = audit(args.root)
    else:
        result = {'scope': 'post-hoc baseline robustness, observed target bank; no LLM arms',
                  'inference_scope': 'exploratory, ten seed units averaged over nine fixed targets per design; Holm over all fifteen contrasts',
                  'designs': {}, 'inference': []}
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            audited = list(executor.map(audit, [args.root/d for d in DESIGNS]))
        for design, data in zip(DESIGNS, audited, strict=True):
            data['by_arm'] = {a: aggregate([c for c in data['cells'] if c['arm'] == a]) for a in ARMS}
            data['nonflat_by_arm'] = {a: aggregate([c for c in data['cells'] if c['arm'] == a and not c['target'].endswith('flat_control')]) for a in ARMS}
            data['by_target'] = {t: {a: aggregate([c for c in data['cells'] if c['target'] == t and c['arm'] == a])
                                    for a in ARMS} for t in data['spec']['targets']}
            result['designs'][design] = data
            result['inference'].extend({'design': design, **r} for r in infer(data['cells']))
            print(design, json.dumps(data['by_arm']), flush=True)
        for row, adjusted in zip(result['inference'], holm_bonferroni(r['exact_sign_flip_p'] for r in result['inference']), strict=True):
            row['holm_p_15_contrasts'] = adjusted
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
