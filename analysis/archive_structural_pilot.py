"""Audit the predeclared four-cell CPU pilot and archive compact evidence."""
import argparse
import json
import math
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    if args.archive.exists():
        raise ValueError('archive already exists')
    rows, digests = [], set()
    for target in ['random_300', 'random_301']:
        for policy in ['random', 'evolutionary']:
            directory = args.source / target / policy
            manifest = json.loads((directory / 'run_manifest.json').read_text())
            summary = json.loads((directory / 'summary.json').read_text())
            trials = [json.loads(line) for line in (directory / 'trials.jsonl').read_text().splitlines()]
            goal = manifest['goal']
            assert manifest['budget'] == 16 and manifest['batch_size'] == 4 and manifest['seed'] == 310
            assert goal['scale'] == 200 and goal['observation_cycles'] == 6774
            assert goal['tolerance'] == 0.10 and goal['loss_version'] == 'fixed-rate-capped-nrmse-v1'
            assert len(trials) == 16 and len({r['trial_id'] for r in trials}) == 16
            best, curve, valid = 1.0, [], 0
            for trial in trials:
                if trial['validity']['valid']:
                    profile = trial['profile']
                    assert profile['valid'] and profile['useful_work'] == 64
                    assert profile['provenance']['clock_edges'] == 6774
                    rates = profile['windowed']
                    assert len(rates) == 8 and all(math.isfinite(x) for x in rates)
                    error = min(1.0, math.sqrt(sum((a-b)**2 for a,b in zip(rates, goal['profile'])) / 8) / 200)
                    assert math.isclose(error, trial['loss'], abs_tol=1e-12)
                    best = min(best, error)
                    valid += 1
                else:
                    assert trial['profile'] is None or not trial['profile']['valid']
                curve.append(best)
            auc = sum((curve[i] + curve[i+1]) / 2 for i in range(15))
            solved = next((i+1 for i,x in enumerate(curve) if x <= 0.1), None)
            assert math.isclose(auc, summary['auc_best_so_far'], abs_tol=1e-12)
            assert summary['valid_trials'] == valid
            assert summary['solved'] == (solved is not None)
            assert summary['evaluations_to_target'] == (solved if solved else 16)
            assert summary['right_censored'] == (solved is None)
            digests.add(manifest['source_digest'])
            rows.append({'reference_name': target, **summary})
    assert len(digests) == 1, 'mixed executable sources in pilot'
    args.archive.mkdir(parents=True)
    for row in rows:
        policy = 'random' if row['policy'] == 'structural-random-v1' else 'evolutionary'
        relative = Path(row['reference_name']) / policy
        destination = args.archive / relative
        destination.mkdir(parents=True)
        for name in ['summary.json', 'trials.jsonl', 'run_manifest.json', 'target_manifest.json', 'best_so_far.json']:
            shutil.copy2(args.source / relative / name, destination / name)
    result = {'scope': 'CPU development plumbing pilot, no statistical superiority claim',
              'audited_cells': 4, 'audited_slots': 64, 'source_digest': next(iter(digests)),
              'rows': rows}
    (args.archive / 'pilot.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
