"""Select seed-400 finalists without inspecting gate-level outcomes."""
import argparse
import hashlib
import json
from pathlib import Path


def choose(trials):
    eligible = [(i, trial) for i, trial in enumerate(trials)
                if trial['validity']['valid'] and trial['loss'] is not None]
    if not eligible:
        return None
    index, trial = min(eligible, key=lambda pair: (pair[1]['loss'], pair[0]))
    return index, sum(t['evaluation_attempts'] for t in trials[:index]), trial


def select(archive):
    report_data = (archive / 'heldout.json').read_bytes()
    report = json.loads(report_data)
    if report['audited_cells'] != 160 or len(report['rows']) != 160:
        raise ValueError('full held-out panel required')
    cases, replays = [], {}
    for row in report['rows']:
        if row['seed'] != 400:
            continue
        design, target, policy = row['design_key'], row['reference_name'], row['policy_alias']
        relative = Path(design) / target / 'seed-400' / policy
        raw = (archive / relative / 'trials.jsonl').read_bytes()
        if hashlib.sha256(raw).hexdigest() != report['artifact_sha256'][str(relative / 'trials.jsonl')]:
            raise ValueError('finalist ledger changed')
        trials = [json.loads(line) for line in raw.splitlines()]
        selected = choose(trials)
        case = {'design': design, 'target': target, 'policy': policy, 'seed': 400,
                'run': str(relative)}
        if selected is None:
            cases.append({**case, 'replay_id': None, 'reason': 'no valid finalist'})
            continue
        index, evaluation_index, trial = selected
        manifest_data = (archive / relative / 'run_manifest.json').read_bytes()
        if hashlib.sha256(manifest_data).hexdigest() != report['artifact_sha256'][str(relative / 'run_manifest.json')]:
            raise ValueError('finalist manifest changed')
        manifest = json.loads(manifest_data)
        replay = {'design': design, 'workload': trial['workload'],
                  'observation_cycles': trial['goal']['observation_cycles'],
                  'contract': manifest['workload_contract'], 'source_digest': manifest['source_digest']}
        ident = hashlib.sha256(json.dumps(replay, sort_keys=True).encode()).hexdigest()
        replays.setdefault(ident, replay)
        source = trial['generation_diagnostics'].get('proposal_source')
        if source is None:
            source = 'model' if policy.endswith(('agent', 'hybrid')) else 'cpu'
        cases.append({**case, 'replay_id': ident, 'proposal_index': index + 1,
                      'evaluation_index': evaluation_index, 'loss': trial['loss'],
                      'proposal_source': source,
                      'activity_profile': trial['profile']})
    if len(cases) != 16 or len({c['run'] for c in cases}) != 16:
        raise ValueError('missing or duplicate seed-400 case')
    return {'rule': 'Best valid trial in seed 400 per design/target/policy; earliest proposal breaks ties.',
            'scope': 'Descriptive finalists selected without gate scores; no proxy-generalization claim.',
            'heldout_report_sha256': hashlib.sha256(report_data).hexdigest(),
            'cases': cases, 'unique_replays': replays}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = select(args.archive)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(f"Selected {len(result['cases'])} cases / {len(result['unique_replays'])} unique replays")


if __name__ == '__main__':
    main()
