"""Offline audit and matched, nonflat-first analysis of the completed Flash panel."""

import argparse
import concurrent.futures
import itertools
import json
import random
from collections import Counter
from pathlib import Path
from statistics import mean

from agcws.core.provenance import file_sha256
from agcws.core.storage import read, write
from agcws.designs.temporal_registry import backend
from agcws.evidence.flash_contract import ARM, matched
from agcws.reporting.accounting.reservations import VERSION, reservation_bound
from agcws.reporting.baselines import ARMS, DESIGNS, aggregate, close
from agcws.reporting.metrics import error, key, max_bin_error, summarize
from agcws.reporting.statistics.inference import holm_bonferroni, paired_permutation_pvalue
from agcws.search.dispatch import Policy
from agcws.search.providers.gemini import MODELS, cost
from agcws.search.providers.schema import provenance


class ReplayMeter:
    """Replay saved provider responses for offline accounting checks."""
    def call(self, directory, arm, contents, schema, identity):
        request = read(directory / 'input.json')
        response = read(directory / 'response.json')
        marker = read(directory / 'request_started.json')
        if request != {'identity': identity, 'payload': contents}:
            raise ValueError('payload is not the deterministic same-cell prior-history rendering')
        if response['identity'] != identity or marker['identity'] != identity:
            raise ValueError('provider identity differs')
        if any(x['schema_provenance'] != provenance(schema) for x in (marker, response)):
            raise ValueError('provider schema differs')
        if not response['usage_unknown']:
            u = response['usage_fields']
            if response['tokens_in'] != u['prompt_token_count'] or response['tokens_out'] != (
                    u['candidates_token_count'] + u['thoughts_token_count']):
                raise ValueError('token accounting differs')
            close(response['estimated_usd'], cost(arm, response['tokens_in'], response['tokens_out']))
        return response


def replay_model_batch(policy, history, directory, identity):
    """Read the frozen Flash format, including its explicitly charged API errors.

    This is not an execution fallback: current execution pauses provider errors.
    Published Flash records retain the accounting rule under which they ran.
    """
    offset = len(history)
    n = min(policy.spec['batch_size'], policy.spec['budget'] - offset)
    goal = {'profile': policy.target, 'scale': policy.spec['scale'],
            'tolerance': policy.spec['tolerance']}
    if policy.spec.get('success_metric') == 'max-bin':
        goal.update(success_metric='max-bin', acceptance=
                    'Every bin must satisfy abs(achieved-target)/scale <= tolerance. '
                    'RMSE remains the ranking score; it is not sufficient for success. '
                    'Use signed per-bin residuals to correct the worst interval.')
    contents = policy.backend.payload(history, goal, n)
    response = ReplayMeter().call(directory, policy.arm, contents, policy.schema, identity)
    if not response.get('api_error') and response['model_version'] != MODELS[policy.arm]:
        raise ValueError('archived provider model version changed')
    decoded = policy.backend.decode(response['raw_text'], n)
    if decoded != read(directory/'decoded.json'):
        raise ValueError('archived decoding differs')
    return [{'slot': offset+j+1, 'program': p['submitted'], 'selected': True,
             'parents': [], 'prediction': p['prediction'],
             'prediction_error': p['prediction_error'], 'api_error': response.get('api_error')}
            for j, p in enumerate(decoded['slots'])]


def summarize_prefixes(history):
    return {str(n): summarize(history[:n], n, .05, stop_on_success=True, success_metric='max-bin')
            for n in (16, 32, 64, 128)}


def inference(cells):
    nonflat = [c for c in cells if not c['target'].endswith('flat_control')]
    seeds = sorted({c['seed'] for c in nonflat})
    rows = []
    for arm in ARMS:
        values = {a: [mean(c['auc'] for c in nonflat if c['arm'] == a and c['seed'] == s)
                      for s in seeds] for a in (ARM, arm)}
        delta = [a-b for a, b in zip(values[ARM], values[arm], strict=True)]
        rng = random.Random(9200)
        boots = sorted(mean(rng.choices(delta, k=len(delta))) for _ in range(10000))
        rows.append({'left': ARM, 'right': arm, 'seeds': seeds, 'seed_mean_differences': delta,
                     'mean_auc_difference': mean(delta), 'bootstrap_95_percent_ci': [boots[249], boots[9749]],
                     'exact_sign_flip_p': paired_permutation_pvalue(values[ARM], values[arm])})
    return rows


def common_valid(left, right):
    a, b = ([t['loss'] for t in rows if t['valid']] for rows in (left, right))
    n = min(len(a), len(b))
    return {'valid_evaluations': n, 'flash_best_error': min(a[:n]) if n else None,
            'baseline_best_error': min(b[:n]) if n else None,
            'scope': 'secondary observed-prefix comparison, affected by early stopping'}


def audit(args):
    design_name, root, baseline_root, published = args
    manifest, reference = read(root/'manifest.json'), read(baseline_root/'manifest.json')
    matched(reference, manifest)
    if file_sha256(baseline_root/'manifest.json') != published['manifest_sha256']:
        raise ValueError('baseline evidence identity differs')
    spec = manifest['spec']
    design = backend(spec['domain'])
    cells, measurements, expected_paths, equal_valid = [], {}, set(), []
    finishes, stages, accounting = Counter(), Counter(), Counter()
    by_baseline = {(c['target'], c['seed'], c['arm']): c for c in published['cells']}
    for target, seed in itertools.product(spec['targets'], spec['seeds']):
        directory = root/'panel'/target/str(seed)/ARM
        expected_paths.add(directory/'complete.json')
        identity = {'target': target, 'seed': seed, 'arm': ARM,
                    'manifest_sha256': file_sha256(root/'manifest.json')}
        if read(directory/'identity.json') != identity:
            raise ValueError('cell identity differs')
        policy = Policy(ARM, seed, spec, spec['targets'][target], manifest['schema'], ReplayMeter())
        history, cell_stages, costs = [], Counter(), Counter()
        for batch in sorted((directory/'batches').iterdir()):
            if any(t['valid'] and t['max_bin_error'] <= .05 for t in history):
                raise ValueError('continued after success')
            required = ['proposals.json', 'trials.json']
            if history:
                required += ['input.json', 'response.json', 'request_started.json', 'decoded.json']
            if any(not (batch/f).is_file() for f in required):
                raise ValueError('incomplete batch')
            batch_identity = {**identity, 'first_slot': len(history)+1}
            proposed = (replay_model_batch(policy, history, batch, batch_identity) if history
                        else policy.propose(history, batch, batch_identity))
            trials = read(batch/'trials.json')
            if proposed != read(batch/'proposals.json') or len(trials) != 2 or len(proposed) != 2:
                raise ValueError('batch does not replay exactly')
            if history:
                response, marker = read(batch/'response.json'), read(batch/'request_started.json')
                reserved = marker['reservation_usd']
                amount = response['estimated_usd'] if not response['usage_unknown'] else reserved
                bound = reservation_bound(response, reserved, ARM) if response['usage_unknown'] else amount
                costs['known_usage_estimate_usd'] += response['estimated_usd'] or 0
                costs['original_liability_usd'] += amount
                costs['reconciled_conservative_liability_usd'] += bound
                costs['provider_calls'] += 1
                costs['unknown_usage_calls'] += response['usage_unknown']
                costs['api_errors'] += bool(response.get('api_error'))
                costs['provider_wall_seconds'] += response['request_wall_clock_s']
                finishes.update(response['finish_reasons'])
                if (batch/'accounting-v1.json').exists():
                    note = read(batch/'accounting-v1.json')
                    if (note['version'] != VERSION or note['response_sha256'] != file_sha256(batch/'response.json')
                            or note['request_sha256'] != file_sha256(batch/'request_started.json')):
                        raise ValueError('accounting adjustment identity differs')
                    close(note['conservative_liability_usd'], bound)
            for index, (p, t) in enumerate(zip(proposed, trials, strict=True)):
                if any(t.get(k) != v for k, v in p.items()) or t['slot'] != len(history)+index+1:
                    raise ValueError('trial/proposal/slot mismatch')
                if t['valid']:
                    close(t['loss'], error(t['rates'], spec['targets'][target], spec['scale']))
                    close(t['max_bin_error'], max_bin_error(t['rates'], spec['targets'][target], spec['scale']))
                    if t['residual'] != [(a-b)/spec['scale'] for a, b in
                                         zip(t['rates'], spec['targets'][target], strict=True)]:
                        raise ValueError('residual mismatch')
                elif t['loss'] is not None or t['max_bin_error'] is not None:
                    raise ValueError('invalid workload scored')
                else:
                    cell_stages[t['stage']] += 1
                if t.get('cache_id'):
                    cached = read(root/'cache'/t['cache_id']/'result.json')
                    canonical = t.get('canonical_program')
                    if canonical is None:
                        canonical = design.canonical(t['program'])
                    if key({'program': canonical, 'measurement': manifest['measurement_fingerprint']}) != t['cache_id']:
                        raise ValueError('cache key mismatch')
                    if cached['valid'] != t['valid'] or (t['valid'] and cached['profile']['window_rates'] != t['rates']):
                        raise ValueError('cache measurement mismatch')
                    measurements[t['cache_id']] = cached.get('evaluation_s', 0)
            history.extend(trials)
        summary = summarize(history, 128, .05, stop_on_success=True, success_metric='max-bin')
        saved = read(directory/'complete.json')
        if saved['cell'] != identity or any(saved[k] != v for k, v in summary.items()):
            raise ValueError('cell summary mismatch')
        stages.update(cell_stages)
        accounting.update(costs)
        cells.append({**summary, 'target': target, 'seed': seed, 'arm': ARM,
                      'invalid_stages': dict(cell_stages), 'costs': dict(costs),
                      'internal_surrogate_candidates': 0, 'prefixes': summarize_prefixes(history)})
        for arm in ARMS:
            base = baseline_root/'panel'/target/str(seed)/arm
            baseline_trials = [t for f in sorted(base.glob('batches/*/trials.json')) for t in read(f)]
            computed = summarize(baseline_trials, 128, .05, stop_on_success=True, success_metric='max-bin')
            published_cell = by_baseline[target, seed, arm]
            if any(published_cell[k] != v for k, v in computed.items()):
                raise ValueError('published baseline cell differs')
            if [t['program'] for t in history[:2]] != [t['program'] for t in baseline_trials[:2]]:
                raise ValueError('shared initialization differs')
            equal_valid.append({'target': target, 'seed': seed, 'baseline': arm,
                                **common_valid(history, baseline_trials)})
    if expected_paths != set(root.glob('panel/*/*/*/complete.json')):
        raise ValueError('unexpected cell set')
    complete = read(root/'complete.json')
    if complete['cells'] != len(cells) or complete['slots'] != sum(c['charged_slots'] for c in cells):
        raise ValueError('panel totals differ')
    for summary in complete['summaries']:
        ident = summary['cell']
        if summary != read(root/'panel'/ident['target']/str(ident['seed'])/ARM/'complete.json'):
            raise ValueError('panel summary differs')
    failures = [read(f) for f in root.glob('failure-*.json')]
    amended = (root/'accounting-amendment-v1.json').exists()
    if failures and (not amended or any('study cost ceiling reached' not in f['error'] for f in failures)):
        raise ValueError('unexplained runner failure')
    liability_field = 'reconciled_conservative_liability_usd' if amended else 'original_liability_usd'
    if abs(complete['liability_usd'] - accounting[liability_field]) > 1e-7:
        raise ValueError('final budget liability differs')
    all_cells = cells + published['cells']
    arms = (ARM, *ARMS)
    return {'manifest_sha256': file_sha256(root/'manifest.json'), 'spec': spec, 'cells': cells,
            'accounting': dict(accounting), 'reported_run_liability_usd': complete['liability_usd'],
            'finish_reasons': dict(finishes), 'invalid_stages': dict(stages), 'retained_failures': failures,
            'unique_measurements': len(measurements), 'unique_evaluation_wall_seconds': sum(measurements.values()),
            'equal_valid_evaluations': equal_valid,
            'nonflat_by_arm': {a: aggregate([c for c in all_cells if c['arm'] == a and
                                           not c['target'].endswith('flat_control')]) for a in arms},
            'control_by_arm': {a: aggregate([c for c in all_cells if c['arm'] == a and
                                           c['target'].endswith('flat_control')]) for a in arms},
            'by_target': {t: {a: aggregate([c for c in all_cells if c['arm'] == a and c['target'] == t])
                              for a in arms} for t in spec['targets']},
            'inference': inference(all_cells)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--baselines', type=Path, required=True)
    from agcws.evidence.catalog import summary
    parser.add_argument('--baseline-summary', type=Path, default=summary(Path.cwd(), 'baselines'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    baseline = read(args.baseline_summary)
    jobs = [(d, args.root/d, args.baselines/d, baseline['designs'][d]) for d in DESIGNS]
    data = {}
    with concurrent.futures.ProcessPoolExecutor(5) as pool:
        for d, result in zip(DESIGNS, pool.map(audit, jobs), strict=True):
            data[d] = result
            print(d, json.dumps(result['nonflat_by_arm']), flush=True)
    contrasts = [{'design': d, **row} for d in DESIGNS for row in data[d]['inference']]
    for row, p in zip(contrasts, holm_bonferroni(r['exact_sign_flip_p'] for r in contrasts), strict=True):
        row['holm_p_15_contrasts'] = p
    write(args.output, {'scope': 'prospective agent comparison on observed targets; not task-held-out',
                       'baseline_summary_sha256': file_sha256(args.baseline_summary), 'designs': data,
                       'inference': contrasts,
                       'audit_scope': 'deterministic request/response replay, same-cell history, metrics, caches, accounting, matched CPU summaries; no waveform resimulation or provider-internal reasoning audit'})


if __name__ == '__main__':
    main()
