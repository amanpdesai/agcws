"""Read-only accounting and paired analysis for the post-hoc phase-GA extension."""

import argparse
import collections
import hashlib
import math
import random
import re
import statistics
from pathlib import Path

from agcws.pipeline.ibex.program import allocation, canonical, interpret, random_program
from agcws.pipeline.metrics import key
from agcws.pipeline.policies.phase import phase_ga
from agcws.pipeline.storage import write
from analysis.accounting_audit import equivalent, read
from analysis.accounting_math import paired, prefix, rms


def holm(values):
    result, previous = {}, 0.0
    for index, (name, value) in enumerate(sorted(values.items(), key=lambda p: (p[1], p[0]))):
        previous = max(previous, min(1.0, (len(values) - index) * value))
        result[name] = previous
    return result


def aggregate(cells, seeds):
    arms = sorted({c["arm"] for c in cells})
    by_budget = {}
    for n in (16, 32, 64, 128):
        by_budget[str(n)] = {}
        for arm in arms:
            rows = [c["prefixes"][str(n)] for c in cells if c["arm"] == arm]
            by_budget[str(n)][arm] = {
                "cells": len(rows),
                "mean_auc": statistics.mean(r["auc"] for r in rows),
                "mean_auc_per_interval": statistics.mean(r["mean_auc"] for r in rows),
                "solves": sum(r["solved"] for r in rows),
                "mean_censored_slots": statistics.mean(r["evaluations_to_target"] for r in rows),
                "mean_final_loss": statistics.mean(r["final_loss"] for r in rows),
                "valid_slots": sum(r["valid_slots"] for r in rows),
            }
    contrasts = {}
    for left, right in (("pro-4096", "phase-ga"), ("phase-ga", "phase-random")):
        differences = []
        for seed in seeds:
            means = {
                arm: statistics.mean(
                    c["prefixes"]["128"]["auc"]
                    for c in cells
                    if c["arm"] == arm and c["seed"] == seed
                )
                for arm in (left, right)
            }
            differences.append(means[left] - means[right])
        contrasts[left + " minus " + right] = paired(differences)
    adjusted = holm({k: v["two_sided_exact_sign_flip_p"] for k, v in contrasts.items()})
    for name, value in contrasts.items():
        value["holm_two_contrasts_p"] = adjusted[name]
    return by_budget, contrasts


def audit(root, historical, gate):
    complete = read(root / "complete.json")
    manifest = read(root / "manifest.json")
    spec = manifest["spec"]
    if (complete["cells"], complete["slots"], complete["liability_usd"]) != (18, 2304, 0):
        raise ValueError("expected complete CPU-only 18-cell/2304-slot panel")
    if spec["policies"] != ["phase-ga"] or spec["budget"] != 128 or spec["batch_size"] != 2:
        raise ValueError("wrong frozen control or budget")
    gate_completion = read(gate / "complete.json")
    if gate_completion["passed"] is not True or gate_completion["cases"] != 7:
        raise ValueError("live equivalence gate not passed")
    frozen = read(historical / "manifest.json")
    targets = read(historical / "targets.json")
    if (
        spec["seeds"] != frozen["seeds"]
        or spec["scale"] != frozen["scale"]
        or spec["tolerance"] != frozen["tolerance"]
        or spec["targets"] != {t["id"]: t["rates"] for t in targets}
    ):
        raise ValueError("confirmation task differs")
    for forbidden in ("**/request_started.json", "**/response.json"):
        if list(root.glob(forbidden)):
            raise ValueError("model artifacts in CPU-only study")
    inputs, cells, all_rows, cache_records = {}, [], {}, {}

    def source(path):
        name = (
            "run/" + str(path.relative_to(root))
            if path.is_relative_to(root)
            else "historical/" + str(path.relative_to(historical))
        )
        inputs[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return read(path)

    for path in (
        root / "manifest.json",
        root / "complete.json",
        historical / "manifest.json",
        historical / "targets.json",
    ):
        source(path)
    for target in targets:
        for seed in spec["seeds"]:
            directory = root / "panel" / target["id"] / str(seed) / "phase-ga"
            rng, rows = random.Random(seed), []
            old_random = source(
                historical / "panel" / target["id"] / str(seed) / "phase-random/complete.json"
            )
            for first in range(1, 129, 2):
                batch = directory / "batches" / f"{first:03}"
                proposals = source(batch / "proposals.json")
                trials = source(batch / "trials.json")
                if [r["slot"] for r in trials] != [first, first + 1] or len(proposals) != 2:
                    raise ValueError("missing or extra charged slot")
                for proposal, row in zip(proposals, trials, strict=True):
                    slot = row["slot"]
                    program, note = (
                        (random_program(rng), {"parents": []})
                        if first == 1
                        else phase_ga(rng, slot, rows)
                    )
                    expected = {
                        "slot": slot,
                        "program": program,
                        "selected": True,
                        "parents": note["parents"],
                    }
                    if proposal != expected or any(row[k] != v for k, v in expected.items()):
                        raise ValueError("proposal generation or parents differ")
                    if first == 1 and program != old_random["trials"][slot - 1]["program"]:
                        raise ValueError("shared charged initialization differs")
                    identifier = row["cache_id"]
                    if identifier != key(
                        {
                            "program": canonical(program),
                            "measurement": manifest["measurement_fingerprint"],
                        }
                    ):
                        raise ValueError("cache fingerprint differs")
                    base = root / "cache" / identifier
                    if identifier not in cache_records:
                        record = source(base / "result.json")
                        cache_records[identifier] = record
                        if source(base / "program.json") != canonical(program):
                            raise ValueError("cached program differs")
                        if record["valid"]:
                            functional = source(base / "run/functional.json")
                            expected_state = interpret(program)
                            if (
                                functional["expected"] != expected_state
                                or not functional["functional_ok"]
                            ):
                                raise ValueError("reference computation differs")
                            log = base / "run/ibex_simple_system.log"
                            inputs["run/" + str(log.relative_to(root))] = hashlib.sha256(
                                log.read_bytes()
                            ).hexdigest()
                            state = re.search(r"AGCWS_STATE ([0-9A-Fa-f ]+)\n", log.read_text())
                            if (
                                not state
                                or [int(x, 16) for x in state[1].split()]
                                != expected_state["registers"] + expected_state["memory"]
                            ):
                                raise ValueError("observed architectural state differs")
                            profile = source(base / "run/profile.json")
                            if profile != record["profile"]:
                                raise ValueError("profile cache differs")
                    record = cache_records[identifier]
                    for field in (
                        "valid",
                        "stage",
                        "reason",
                        "allocation",
                        "execution",
                        "feedback",
                    ):
                        if record.get(field) != row.get(field):
                            raise ValueError("cache/trial differs: " + field)
                    if allocation(program) != row["allocation"] or sum(row["allocation"]) != 4096:
                        raise ValueError("work allocation differs")
                    if row["valid"]:
                        p = record["profile"]
                        rates = [v / 25000 for v in p["window_bit_transitions"]]
                        if (
                            rates != row["rates"]
                            or p["window_rates"] != rates
                            or p["clock_edges"] != 200000
                            or p["end_tick"] - p["begin_tick"] != 400000
                            or p["unknown_events"] != 0
                        ):
                            raise ValueError("measurement window or rate differs")
                        if not equivalent(rms(rates, target["rates"], spec["scale"]), row["loss"]):
                            raise ValueError("loss differs")
                    elif row["loss"] is not None or row["rates"] is not None:
                        raise ValueError("invalid proposal scored")
                rows.extend(trials)
            published = source(directory / "complete.json")
            result = prefix(rows, 128, spec["tolerance"])
            if not equivalent({k: published[k] for k in result}, result):
                raise ValueError("saved metrics differ from raw slots")
            for arm in ("phase-ga", "phase-random", "pro-4096"):
                records = (
                    rows
                    if arm == "phase-ga"
                    else source(
                        historical / "panel" / target["id"] / str(seed) / arm / "complete.json"
                    )["trials"]
                )
                all_rows[target["id"], seed, arm] = records
                cells.append(
                    {
                        "target": target["id"],
                        "seed": seed,
                        "arm": arm,
                        "validity": dict(
                            collections.Counter(r["stage"] or "VALID" for r in records)
                        ),
                        "prefixes": {
                            str(n): {
                                k: v
                                for k, v in prefix(records, n, spec["tolerance"]).items()
                                if k != "curve"
                            }
                            for n in (16, 32, 64, 128)
                        },
                    }
                )
    actual_cache = {p.parent.name for p in (root / "cache").glob("*/result.json")}
    if actual_cache != cache_records.keys():
        raise ValueError("unaccounted cached measurements")
    budgets, contrasts = aggregate(cells, spec["seeds"])
    equal_valid = []
    for target in targets:
        for seed in spec["seeds"]:
            valid = {
                a: [r for r in all_rows[target["id"], seed, a] if r["valid"]]
                for a in ("phase-ga", "phase-random", "pro-4096")
            }
            n = min(map(len, valid.values()))
            equal_valid.append(
                {
                    "target": target["id"],
                    "seed": seed,
                    "common_valid_count": n,
                    "best_errors": {
                        a: min(r["loss"] for r in rows[:n]) if n else None
                        for a, rows in valid.items()
                    },
                }
            )
    return {
        "scope": "post-hoc untuned robustness extension; six seed units conditional on three observed targets",
        "budgets": budgets,
        "contrasts": contrasts,
        "cells": cells,
        "equal_valid_secondary": equal_valid,
        "inputs_sha256": inputs,
        "accounting": {
            "new_slots": 2304,
            "new_model_calls": 0,
            "model_usd": 0,
            "unique_measurements": len(cache_records),
            "cache_hits": sum(
                r["cache_hit"]
                for (t, s, a), rows in all_rows.items()
                if a == "phase-ga"
                for r in rows
            ),
            "sum_unique_evaluation_wall_s": math.fsum(
                r["evaluation_s"] for r in cache_records.values()
            ),
            "container_cpu_seconds": None,
        },
        "limitations": [
            "Holm two-comparison p cannot be below 0.0625 with six seed units",
            "equal-valid analysis is secondary, not a change to proposal accounting",
            "GNU time measures host orchestration/client CPU, not container CPU",
            "sum of evaluation wall durations is not CPU time or total study wall time",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "historical", "gate", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    write(args.out, audit(args.root.resolve(), args.historical.resolve(), args.gate.resolve()))


if __name__ == "__main__":
    main()
