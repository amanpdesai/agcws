"""Independent complete-grid audit and development-family selection."""
import argparse
import hashlib
import itertools
import json
import math
import shutil
from collections import Counter
from pathlib import Path
from statistics import mean

NAMES = {
    'random': 'structural-random-v1', 'evolutionary': 'structural-evolution-v1',
    'population-evolution': 'structural-population-evolution-v1',
    'edit-agent': 'structural-edit-agent-v2', 'edit-hybrid': 'structural-edit-hybrid-v2',
    'population-agent': 'structural-population-agent-v1',
    'population-hybrid': 'structural-population-hybrid-v1',
}
FILES = ('summary.json', 'trials.jsonl', 'run_manifest.json', 'target_manifest.json', 'best_so_far.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit_cell(cell, design, target, seed, policy, budget):
    manifest = json.loads((cell / 'run_manifest.json').read_text())
    summary = json.loads((cell / 'summary.json').read_text())
    reference = json.loads((cell / 'target_manifest.json').read_text())
    rows = [json.loads(line) for line in (cell / 'trials.jsonl').read_text().splitlines()]
    goal = manifest['goal']
    horizon, scale, work = (6774, 200, 64) if design == 'aes' else (12000, 40, 4096)
    require(manifest['policy'] == summary['policy'] == NAMES[policy], 'policy mismatch')
    require(manifest['seed'] == summary['seed'] == seed, 'seed mismatch')
    require(manifest['budget'] == summary['budget'] == budget and manifest['batch_size'] == 4,
            'budget mismatch')
    require(reference['reference_name'] == target and reference['design'] == design, 'target mismatch')
    require(goal == reference['goal'] and goal['scale'] == scale
            and goal['observation_cycles'] == horizon and goal['windows'] == 8
            and goal['tolerance'] == 0.1 and goal['loss_version'] == 'fixed-rate-capped-nrmse-v1',
            'goal mismatch')
    require(len(rows) == budget and len({r['trial_id'] for r in rows}) == budget, 'incomplete ledger')
    best, curve, valid = 1.0, [], 0
    for row in rows:
        require(row['policy'] == NAMES[policy] and row['seed'] == seed and row['goal'] == goal,
                'trial identity mismatch')
        if row['validity']['valid']:
            profile = row['profile']
            require(profile['valid'] and profile['useful_work'] == work
                    and profile['provenance']['clock_edges'] == horizon, 'work/window mismatch')
            rates = profile['windowed']
            require(len(rates) == 8 and all(math.isfinite(x) and x >= 0 for x in rates), 'bad rates')
            if design == 'dma':
                obs = profile['provenance']['observed']
                require(obs['read_descriptors'] == obs['write_completions'] == 64, 'incomplete DMA work')
            loss = min(1.0, math.sqrt(mean((a - b)**2 for a, b in zip(rates, goal['profile']))) / scale)
            require(math.isclose(loss, row['loss'], abs_tol=1e-12), 'incorrect trial loss')
            best = min(best, loss)
            valid += 1
        else:
            require(row['profile'] is None or not row['profile']['valid'], 'invalid trial scored')
        curve.append(best)
    auc = sum((a + b) / 2 for a, b in itertools.pairwise(curve))
    solved = next((i + 1 for i, loss in enumerate(curve) if loss <= 0.1), None)
    require(math.isclose(auc, summary['auc_best_so_far'], abs_tol=1e-12), 'incorrect AUC')
    require(summary['solved'] == (solved is not None)
            and summary['evaluations_to_target'] == (solved or budget)
            and summary['right_censored'] == (solved is None), 'incorrect censoring')
    require(summary['valid_trials'] == valid and summary['proposal_slots'] == budget, 'incorrect counts')
    failures = Counter(row['validity']['stage'] for row in rows if not row['validity']['valid'])
    require(all(stage in summary['validity_failures'] for stage in failures)
            and all(failures[stage] == count for stage, count in summary['validity_failures'].items()),
            'incorrect rejection counts')
    require(summary['unknown_usage_batches'] == sum(
        bool(row['generation_diagnostics'].get('usage_unknown')) for row in rows), 'unknown usage mismatch')
    for field in ('tokens_in', 'tokens_out', 'est_cost_usd'):
        require(math.isclose(sum(row[field] for row in rows), summary[field], abs_tol=1e-12), field)
    if manifest['model']:
        price = manifest['pricing']
        expected = (summary['tokens_in'] * float(price['INPUT_USD_PER_MILLION'])
                    + summary['tokens_out'] * float(price['OUTPUT_USD_PER_MILLION'])) / 1e6
        require(math.isclose(expected, summary['est_cost_usd'], abs_tol=1e-12), 'pricing mismatch')
    timing = {}
    for key in ('wall_clock_s', 'generation_wall_clock_s'):
        require(all(math.isfinite(row[key]) and row[key] >= 0 for row in rows), 'invalid ledger timing')
        timing[key] = sum(row[key] for row in rows)
    return {'design': design, 'reference_name': target, 'policy_alias': policy,
            **summary, 'ledger_timing_s': timing}, manifest, reference


def build(source):
    panel = json.loads((source / 'panel_manifest.json').read_text())
    spec = panel['spec']
    require(spec['phase'] == 'development', 'not a development panel')
    require(set(spec['policies']) == set(NAMES), 'incomplete policy selection panel')
    require(spec['designs'] == ['aes', 'dma'] and spec['targets'] == ['random_300', 'random_301']
            and spec['seeds'] == [315, 316, 317] and spec['budget'] == 16 and spec['batch_size'] == 4,
            'panel differs from declared development protocol')
    rows, hashes, conditions, configurations, digests = [], {}, {}, {}, set()
    for design, target, seed, policy in itertools.product(
            spec['designs'], spec['targets'], spec['seeds'], spec['policies']):
        relative = Path(design) / target / f'seed-{seed}' / policy
        cell = source / relative
        row, manifest, reference = audit_cell(cell, design, target, seed, policy, spec['budget'])
        condition = (manifest['goal'], manifest['workload_contract'], reference['source_sha256'])
        key = design, target
        require(key not in conditions or conditions[key] == condition, 'mixed target conditions')
        conditions[key] = condition
        if manifest['model']:
            configuration = {k: manifest[k] for k in ('model', 'prompt_hash', 'sampling', 'pricing')}
            require(not configurations or configurations == configuration, 'mixed agent configuration')
            configurations = configuration
        digests.add(manifest['source_digest'])
        rows.append(row)
        for name in FILES:
            path = relative / name
            hashes[str(path)] = hashlib.sha256((source / path).read_bytes()).hexdigest()
    require(len(digests) == 1, 'mixed source versions')
    scores = {family: mean(row['auc_best_so_far'] for row in rows if row['policy_alias'] in policies)
              for family, policies in [('best-eight', ['edit-agent', 'edit-hybrid']),
                                       ('peak-window-population', ['population-agent', 'population-hybrid'])]}
    selected = min(scores, key=scores.get)
    return {'scope': 'Development selection only; fresh held-out evaluation still required.',
            'panel': panel, 'source_digest': next(iter(digests)), 'agent_configuration': configurations,
            'family_scores': scores, 'selected_family': selected, 'rows': rows, 'artifact_sha256': hashes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    require(not args.archive.exists(), 'archive exists')
    result = build(args.source)
    args.archive.mkdir(parents=True)
    for name in result['artifact_sha256']:
        destination = args.archive / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.source / name, destination)
    shutil.copy2(args.source / 'panel_manifest.json', args.archive / 'panel_manifest.json')
    (args.archive / 'development.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['family_scores']))
    print(f"Selected family: {result['selected_family']}")


if __name__ == '__main__':
    main()
