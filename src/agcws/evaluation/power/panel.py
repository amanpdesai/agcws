"""Bounded, restartable finalist replay with immutable collection identity."""

import argparse
import concurrent.futures
import fcntl
import json
from pathlib import Path

from agcws.core.storage import ensure, read, write
from agcws.designs.aes.gls import sha
from agcws.evaluation.power.finalists import run
from agcws.studies.finalists import verify


def collection_identity(plan, syntheses, runtime, minimum_coverage):
    verify(plan)
    domains = {c["domain"] for c in plan["cases"]}
    if domains - syntheses.keys():
        raise ValueError(f"missing synthesis mapping: {sorted(domains - syntheses.keys())}")
    if not 0 < minimum_coverage <= 1:
        raise ValueError("annotation threshold must be in (0,1]")
    syntheses = {k: Path(v).resolve(strict=True) for k, v in syntheses.items()}
    return {
        "version": "power-collection-v1", "plan_sha256": plan["sha256"],
        "runtime": str(runtime.resolve(strict=True)) if runtime else None,
        "minimum_coverage": minimum_coverage,
        "syntheses": {k: {"path": str(v), "manifest_sha256": sha(v / "manifest.json")}
                       for k, v in sorted(syntheses.items())},
        "validation_sources": {str(p): sha(p) for directory in (
            "src/agcws/evaluation", "src/agcws/designs", "src/agcws/reporting")
            for p in sorted(Path(directory).rglob("*.py"))},
    }


class Collection:
    """Locked collection with independently checkpointed cases."""

    def __init__(self, plan, syntheses, out, *, runtime=None, minimum_coverage=.99,
                 amendment=None):
        self.plan, self.out = plan, Path(out)
        self.syntheses = {k: Path(v).resolve(strict=True) for k, v in syntheses.items()}
        self.runtime, self.minimum_coverage = runtime, minimum_coverage
        self.identity = collection_identity(plan, syntheses, runtime, minimum_coverage)
        self.amendment = amendment

    def __enter__(self):
        self.out.mkdir(parents=True, exist_ok=True)
        self.lock = (self.out / 'runner.lock').open('a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            path = self.out / 'collection.json'
            if path.exists() and read(path) != self.identity and self.amendment:
                prior = read(path)
                expected = json.loads(json.dumps(prior))
                name = 'src/agcws/evaluation/power/panel.py'
                changes = self.amendment.get('sources', {name: self.amendment.get('panel')})
                allowed = {name, 'src/agcws/designs/redmule/container.py',
                           'src/agcws/evaluation/simulation/cached_verilator.py',
                           'src/agcws/evaluation/power/finalists.py',
                           'src/agcws/evaluation/power/windows.py',
                           'src/agcws/reporting/power_reference.py'}
                if not changes or set(changes) - allowed:
                    raise ValueError('unsupported execution amendment')
                for source, change in changes.items():
                    if (not change or
                            prior['validation_sources'].get(source) != change['before'] or
                            self.identity['validation_sources'].get(source) != change['after']):
                        raise ValueError('execution amendment does not match code')
                    expected['validation_sources'][source] = change['after']
                if expected != self.identity:
                    raise ValueError('orchestration amendment cannot change measurement identity')
                ensure(self.out / f"orchestration-{self.identity['validation_sources'][name]}.json",
                       {'original_identity_sha256': sha(path), 'identity': self.identity,
                        'amendment': self.amendment})
            else:
                ensure(path, self.identity)
        except BaseException:
            self.lock.close()
            raise
        return self

    def __exit__(self, *exc):
        self.lock.close()

    def __getstate__(self):
        # The coordinator owns the collection lock for the lifetime of its pool.
        # Spawned workers receive immutable configuration, never the lock handle.
        return {name: value for name, value in self.__dict__.items() if name != 'lock'}

    def retained(self, case):
        directory = self.out / case['id']
        complete = directory / 'complete.json'
        if not complete.exists():
            return None
        receipt = read(complete)
        measurement = directory / receipt['attempt'] / 'measurement.json'
        if (measurement.parent.parent != directory or
                sha(measurement) != receipt['measurement_sha256']):
            raise ValueError('completed power replay changed')
        result = read(measurement)
        if result['case_id'] != case['id'] or result['plan_sha256'] != self.plan['sha256']:
            raise ValueError('completed power replay belongs to another case')
        return {'case': case['id'], 'status': 'retained', 'path': str(measurement.parent)}

    def cell(self, case):
        retained = self.retained(case)
        if retained:
            return retained
        directory = self.out / case['id']
        directory.mkdir(exist_ok=True)
        numbers = [int(p.name.split('-')[1]) for p in directory.glob('attempt-*')]
        attempt = directory / f'attempt-{max(numbers, default=0) + 1:03}'
        try:
            run(self.plan, case['id'], self.syntheses[case['domain']], attempt,
                minimum_coverage=self.minimum_coverage, runtime=self.runtime)
        except Exception as exc:
            attempt.mkdir(exist_ok=True)
            write(attempt / 'failure.json', {'type': type(exc).__name__, 'message': str(exc)})
            return {'case': case['id'], 'status': 'failed', 'path': str(attempt), 'error': str(exc)}
        write(directory / 'complete.json',
              {'attempt': attempt.name, 'measurement_sha256': sha(attempt / 'measurement.json')})
        return {'case': case['id'], 'status': 'measured', 'path': str(attempt)}

    def finish(self, results, preflight):
        report = {'plan_sha256': self.plan['sha256'],
                  'cases': sorted(results, key=lambda r: r['case']),
                  'omitted': self.plan['omitted'], 'preflight': preflight,
                  'all_passed': all(r['status'] in ('retained', 'measured') for r in results)}
        write(self.out / f"pass-{len(list(self.out.glob('pass-*.json'))) + 1:03}.json", report)
        return report


def collect(plan, syntheses, out, *, workers=1, runtime=None, minimum_coverage=.99,
            preflight=False):
    if workers < 1:
        raise ValueError('workers must be positive')
    with Collection(plan, syntheses, out, runtime=runtime,
                    minimum_coverage=minimum_coverage) as collection:

        remaining = plan["cases"]
        results = []
        if preflight and remaining:
            first = collection.cell(remaining[0])
            results.append(first)
            print(json.dumps({"completed": 1, "total": len(remaining), **first}), flush=True)
            remaining = remaining[1:]
            if first["status"] == "failed":
                results.extend({"case": c["id"], "status": "deferred",
                                "error": "First-case readiness replay failed"} for c in remaining)
                remaining = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(collection.cell, case) for case in remaining]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                print(json.dumps({"completed": len(results), "total": len(plan["cases"]), **result}), flush=True)
        return collection.finish(results, preflight)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--syntheses", type=Path, required=True, help="JSON mapping domain to synthesis directory")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--minimum-coverage", type=float, default=.99)
    parser.add_argument("--preflight", action="store_true",
                        help="Require the first planned replay to pass before admitting the rest")
    args = parser.parse_args(argv)
    result = collect(read(args.plan), read(args.syntheses), args.out, workers=args.workers,
                     runtime=args.runtime, minimum_coverage=args.minimum_coverage,
                     preflight=args.preflight)
    if not result["all_passed"]:
        raise SystemExit("power collection retained failures; inspect pass report")


if __name__ == "__main__":
    main()
