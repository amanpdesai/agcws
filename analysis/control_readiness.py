"""Offline historical/current control and compiler equivalence; no RTL simulation."""

import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def probe(fixtures, legacy):
    if legacy:
        from experiments.ibex_depth_v1.metrics import summarize
        from experiments.ibex_temporal_v3.program import allocation, interpret, random_program
        from experiments.ibex_temporal_v4.compiler import assembly
        from experiments.temporal_scaling_v1.baselines import phase_ga
    else:
        from agcws.pipeline.ibex.compiler import assembly
        from agcws.pipeline.ibex.program import allocation, interpret, random_program
        from agcws.pipeline.metrics import summarize
        from agcws.pipeline.policies.phase import phase_ga

    trajectories = []
    operators = set()
    for seed in range(1200, 1206):
        rng, history, records = random.Random(seed), [], []
        for first in range(1, 129, 2):
            batch = []
            for slot in (first, first + 1):
                program, note = (
                    (random_program(rng), {"operator": "initial", "parents": []})
                    if first == 1
                    else phase_ga(rng, slot, history)
                )
                operators.add(note["operator"])
                valid = slot % 11 != 0
                batch.append(
                    {
                        "slot": slot,
                        "valid": valid,
                        "loss": ((slot * 7 + seed) % 31) / 31 if valid else None,
                        "canonical_program": program,
                    }
                )
                records.append(
                    {
                        "slot": slot,
                        "program": program,
                        "note": note,
                        "allocation": allocation(program),
                        "assembly_sha256": hashlib.sha256(assembly(program).encode()).hexdigest(),
                    }
                )
            history.extend(batch)
        trajectories.append(fingerprint(records))
    measured = []
    for cell in fixtures:
        rows = cell["rows"]
        examples = [r for r in rows if r["slot"] in cell["inspect_slots"] and r["valid"]]
        measured.append(
            {
                "prefixes": {str(n): summarize(rows, n, 0.1) for n in (16, 32, 64, 128)},
                "examples": [
                    {
                        "slot": r["slot"],
                        "allocation": allocation(r["canonical_program"]),
                        "expected_state": interpret(r["canonical_program"]),
                        "assembly_sha256": hashlib.sha256(
                            assembly(r["canonical_program"]).encode()
                        ).hexdigest(),
                    }
                    for r in examples
                ],
            }
        )
    return {
        "synthetic_trajectories_sha256": trajectories,
        "synthetic_operators": sorted(operators),
        "archived_fixtures": measured,
    }


def check(repo, archive):
    from agcws.pipeline.archive import extract
    from analysis.accounting_audit import equivalent, read

    fixtures, inputs, replay = [], {}, {}
    for source in sorted((archive / "panel").glob("*/*/*/complete.json")):
        complete = read(source)
        rows = complete["trials"]
        valid = [r for r in rows if r["valid"]]
        slots = sorted(
            {1, 2, valid[0]["slot"], min(valid, key=lambda r: (r["loss"], r["slot"]))["slot"]}
        )
        fixtures.append({"cell": complete["cell"], "rows": rows, "inspect_slots": slots})
        inputs[str(source.relative_to(archive))] = hashlib.sha256(source.read_bytes()).hexdigest()
        if complete["cell"]["seed"] == 1200:
            for role, row in (
                ("first_valid", valid[0]),
                ("best", min(valid, key=lambda r: (r["loss"], r["slot"]))),
            ):
                item = replay.setdefault(
                    row["cache_id"],
                    {
                        "cache_id": row["cache_id"],
                        "program_sha256": fingerprint(row["canonical_program"]),
                        "origins": [],
                    },
                )
                item["origins"].append(
                    {"cell": complete["cell"], "slot": row["slot"], "role": role}
                )
    if len(fixtures) != 36:
        raise ValueError("expected complete 36-cell confirmation fixture panel")
    with tempfile.TemporaryDirectory(prefix="agcws-control-readiness-") as temp:
        old = extract(repo, Path(temp) / "source")
        reports = []
        for root, legacy in ((old, True), (repo, False)):
            command = [sys.executable, str(Path(__file__).resolve()), "--worker"]
            if legacy:
                command.append("--legacy")
            result = subprocess.run(
                command,
                cwd=root,
                input=json.dumps(fixtures),
                text=True,
                capture_output=True,
                check=True,
                env={**os.environ, "PYTHONPATH": os.pathsep.join((str(root), str(root / "src")))},
            )
            reports.append(json.loads(result.stdout))
    if not equivalent(*reports):
        raise ValueError("historical/current control or compiler behavior differs; do not launch")
    return {
        "status": "offline checks passed; live evaluator equivalence not established",
        "fixture_cells": len(fixtures),
        "synthetic_slots": 6 * 128,
        "synthetic_loss": "deterministic mock feedback only, every eleventh slot invalid; not performance evidence",
        "compiler_state_examples": sum(len(c["examples"]) for c in reports[0]["archived_fixtures"]),
        "historical_current_equal": True,
        "live_replay_selection": sorted(replay.values(), key=lambda r: r["cache_id"]),
        "probe": {
            "synthetic_trajectories_sha256": reports[1]["synthetic_trajectories_sha256"],
            "synthetic_operators": reports[1]["synthetic_operators"],
            "archived_fixture_sha256": [
                {"cell": fixture["cell"], "sha256": fingerprint(result)}
                for fixture, result in zip(fixtures, reports[1]["archived_fixtures"], strict=True)
            ],
        },
        "inputs_sha256": inputs,
        "source_sha256": {
            str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(
                [
                    *(repo / "src/agcws/pipeline").rglob("*.py"),
                    repo / "analysis/control_readiness.py",
                    repo / "archive/legacy-source.tar.gz",
                ]
            )
        },
        "remaining_gates": [
            "fresh tool/image/binary identity verification",
            "authorized matched live replay before combining new and historical measurements",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--legacy", action="store_true")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(probe(json.load(sys.stdin), args.legacy), allow_nan=False))
        return
    if args.archive is None or args.out is None:
        parser.error("--archive and --out required")
    report = check(Path.cwd().resolve(), args.archive.resolve())
    with args.out.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
