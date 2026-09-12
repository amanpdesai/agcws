"""All-record independent reconciliation; reads verified evidence, never executes policies."""

import argparse
import collections
import functools
import gzip
import hashlib
import json
import math
import statistics
import tarfile
from pathlib import Path

from analysis.accounting_math import charge, paired, prefix, rms


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    if isinstance(value, list):
        return [canonical(v) for v in value]
    return int(value) if isinstance(value, float) and value.is_integer() else value


def program_id(program, fingerprint):
    encoded = json.dumps(
        {"program": canonical(program), "measurement": fingerprint}, sort_keys=True
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def equivalent(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    return a == b


def audit(root, repo):
    m, targets, panel = [
        read(root / f) for f in ("manifest.json", "targets.json", "search_manifest.json")
    ]
    checks, discrepancies, observations = collections.Counter(), [], collections.Counter()

    def check(ok, label, location):
        checks[label] += 1
        if not ok:
            discrepancies.append({"check": label, "location": location})

    expected = [
        {"target": t["id"], "seed": s, "arm": a}
        for t in targets
        for s in m["seeds"]
        for a in m["arms"]
    ]
    check(panel["cells"] == expected, "panel_cartesian_product", "search_manifest")
    for key, path in [("manifest_sha256", "manifest.json"), ("targets_sha256", "targets.json")]:
        check(panel[key] == digest(root / path), "search_identity", key)
    for key, path in [("schema_sha256", "schema.json"), ("parent_sha256", "parent_manifest.json")]:
        check(m[key] == digest(root / path), "frozen_identity", key)
    with tarfile.open(repo / "archive/legacy-source.tar.gz") as archive:
        for name, want in m["sources"].items():
            source = archive.extractfile(name)
            check(hashlib.sha256(source.read()).hexdigest() == want, "original_source_hash", name)

    @functools.lru_cache(maxsize=None)
    def evaluation(identifier):
        base = root / "evaluations" / identifier
        return read(base / "result.json.gz"), read(base / "program.json.gz")

    uses = collections.defaultdict(list)
    all_rows, cells, requests, expected_request_paths = {}, [], [], set()
    static_payload = collections.defaultdict(set)
    exposed_history, exposed_notebook = 0, 0
    witnesses = read(root / "witnesses.json")
    witness_programs = {json.dumps(canonical(w["program"]), sort_keys=True) for w in witnesses}
    witness_ids = {w["cache_id"] for w in witnesses}

    def measurement(row, target, location):
        identifier = row.get("cache_id")
        if identifier:
            uses[identifier].append(
                {"location": location, "hit": row["cache_hit"], "valid": row["valid"]}
            )
            record, program = evaluation(identifier)
            check(
                identifier == program_id(row["program"], m["measurement_fingerprint"]),
                "cache_key",
                location,
            )
            check(
                program == canonical(row["program"]) == row["canonical_program"],
                "measured_program",
                location,
            )
            for key in (
                "valid",
                "stage",
                "reason",
                "allocation",
                "feedback",
                "execution",
                "evaluation_s",
            ):
                check(equivalent(record.get(key), row.get(key)), "cached_record_" + key, location)
        else:
            check(not row["valid"] and not row["cache_hit"], "unmeasured_rejection", location)
        if not row["valid"]:
            check(
                row["loss"] is None and row["rates"] is None and row["residual"] is None,
                "invalid_no_score",
                location,
            )
            return dict(row, loss=None)
        base = root / "evaluations" / identifier / "run"
        profile = read(base / "profile.json.gz")
        check(profile == record["profile"], "profile_record_identity", location)
        measured = [count / 25000 for count in profile["window_bit_transitions"]]
        check(measured == profile["window_rates"] == row["rates"], "integer_bin_rates", location)
        check(
            profile["clock_edges"] == 200000
            and profile["end_tick"] - profile["begin_tick"] == 400000
            and profile["unknown_events"] == 0,
            "measurement_window",
            location,
        )
        check(sum(row["allocation"]) == 4096, "operation_floor", location)
        value = rms(measured, target, m["scale"])
        check(equivalent(value, row["loss"]), "loss_from_measured_counts", location)
        check(
            equivalent([(a - b) / m["scale"] for a, b in zip(measured, target)], row["residual"]),
            "signed_residual",
            location,
        )
        return dict(row, loss=value)

    qualification = []
    chosen = []
    check(
        [w["slot"] for w in witnesses] == list(range(1, 25)),
        "all_construction_attempts",
        "witnesses",
    )
    for w in witnesses:
        measurement(w, [0.0] * 8, f"construction/{w['slot']}")
        floor = statistics.pstdev(w["rates"]) / m["scale"] if w["valid"] else None
        distances = [rms(w["rates"], t["rates"], m["scale"]) for t in chosen] if w["valid"] else []
        qualifies = (
            w["valid"]
            and floor >= m["minimum_constant_floor"]
            and all(d >= m["minimum_pair_distance"] for d in distances)
        )
        selected = bool(qualifies and len(chosen) < m["target_count"])
        qualification.append(
            {
                "slot": w["slot"],
                "valid": w["valid"],
                "floor": floor,
                "distances_to_previously_selected": distances,
                "selected": selected,
            }
        )
        if selected:
            chosen.append(
                {
                    "id": f"target_{len(chosen)}",
                    "rates": w["rates"],
                    "constant_floor": floor,
                    "witness_slot": w["slot"],
                    "witness_cache_id": w["cache_id"],
                }
            )
    check(equivalent(chosen, targets), "first_qualifying_targets", "targets")

    for cell in expected:
        target = next(t for t in targets if t["id"] == cell["target"])
        location = f"panel/{cell['target']}/{cell['seed']}/{cell['arm']}"
        directory = root / location
        complete = read(directory / "complete.json")
        check(complete["cell"] == cell, "cell_identity", location)
        rows, regenerated = [], []
        check(
            sorted(p.name for p in (directory / "batches").iterdir())
            == [f"{i:03}" for i in range(1, 129, 2)],
            "exact_batch_directories",
            location,
        )
        for first in range(1, 129, 2):
            batch = directory / "batches" / f"{first:03}"
            where = f"{location}/batches/{first:03}"
            sent, decoded, trials = [
                read(batch / (f + ".json.gz")) for f in ("input", "decoded", "trials")
            ]
            ident = {
                "cell": cell,
                "first_slot": first,
                "search_sha256": digest(root / "search_manifest.json"),
            }
            check(sent["identity"] == ident, "input_identity", where)
            check(
                len(trials) == 2 and [r["slot"] for r in trials] == [first, first + 1],
                "requested_slots",
                where,
            )
            model = cell["arm"] == "pro-4096" and first > 1
            request_files = {p.name for p in batch.iterdir()}
            allowed = {"input.json.gz", "decoded.json.gz", "trials.json.gz"}
            if model:
                allowed |= {"request_started.json.gz", "response.json.gz"}
                expected_request_paths.add(where + "/request_started.json.gz")
                started, response = [
                    read(batch / (f + ".json.gz")) for f in ("request_started", "response")
                ]
                check(
                    started["identity"] == response["identity"] == ident,
                    "request_response_identity",
                    where,
                )
                reservation = (200000 * 1.25 + 16384 * 10) / 1e6
                check(
                    equivalent(reservation, started["reservation_usd"]),
                    "request_reservation",
                    where,
                )
                billed = charge(response, reservation)
                if not response["usage_unknown"]:
                    check(
                        equivalent(billed["known"], response["estimated_usd"]),
                        "cost_from_usage",
                        where,
                    )
                    check(
                        response["model_version"] == m["models"]["pro-4096"]["model"],
                        "model_version",
                        where,
                    )
                observations[
                    "api_errors" if response.get("api_error") else "successful_responses"
                ] += 1
                if response.get("api_error"):
                    observations["api_" + response["api_error"]["message"].split(":")[0]] += 1
                try:
                    parsed = json.loads(response["raw_text"])
                    candidates = parsed.get("candidates") if isinstance(parsed, dict) else None
                except ValueError:
                    candidates = None
                observations[
                    "raw_batch_size_"
                    + str(len(candidates) if isinstance(candidates, list) else "unparseable")
                ] += 1
                candidates = (
                    candidates if isinstance(candidates, list) and len(candidates) <= 2 else []
                )
                check(sent["cpu_candidates"] is None, "no_model_cpu_replacement", where)
                value = json.loads(sent["payload"])
                check(
                    value["goal"]
                    == {
                        "profile": target["rates"],
                        "scale": m["scale"],
                        "tolerance": m["tolerance"],
                    }
                    and value["batch_size"] == 2,
                    "payload_goal_budget",
                    where,
                )
                check(
                    set(value)
                    == {
                        "batch_size",
                        "experiment_notebook",
                        "goal",
                        "history",
                        "response_contract",
                        "schema",
                        "semantics",
                        "system_prompt",
                    },
                    "payload_fields",
                    where,
                )
                for k in ("response_contract", "schema", "semantics", "system_prompt"):
                    static_payload[k].add(
                        hashlib.sha256(json.dumps(value[k], sort_keys=True).encode()).hexdigest()
                    )
                top = sorted((r for r in rows if r["valid"]), key=lambda r: (r["loss"], r["slot"]))[
                    :4
                ]
                check(
                    {h["slot"] for h in value["history"]} == {r["slot"] for r in top + rows[-4:]},
                    "history_selection",
                    where,
                )
                for h in value["history"]:
                    exposed_history += 1
                    prior = next((r for r in rows if r["slot"] == h["slot"]), None)
                    check(
                        prior is not None
                        and all(equivalent(prior.get(k), v) for k, v in h.items()),
                        "history_same_cell_prior",
                        where,
                    )
                    check(
                        json.dumps(canonical(h["program"]), sort_keys=True) not in witness_programs,
                        "no_witness_program_in_history",
                        where,
                    )
                expected_notes = [r for r in rows if r["proposal_mode"] != "initial"][-6:]
                check(
                    [n["slot"] for n in value["experiment_notebook"]]
                    == [r["slot"] for r in expected_notes],
                    "notebook_selection",
                    where,
                )
                for note, prior in zip(value["experiment_notebook"], expected_notes):
                    exposed_notebook += 1
                    check(
                        equivalent(note, prior["prediction_assessment"]),
                        "notebook_same_cell_prior",
                        where,
                    )
                for term in (
                    "witness_cache_id",
                    "witness_slot",
                    "construction_seed",
                    "scheduled-four-phase",
                ):
                    check(
                        term not in sent["payload"],
                        "no_privileged_payload_term",
                        where + "/" + term,
                    )
                check(
                    len(sent["payload"].encode())
                    + len(json.dumps(read(root / "schema.json")).encode())
                    + 4096
                    <= m["payload_bound"],
                    "request_size_bound",
                    where,
                )
                requests.append(
                    {
                        "path": where,
                        "started": started["started_unix"],
                        "duration_s": response["request_wall_clock_s"],
                        **billed,
                        "response_raw_sha256": hashlib.sha256(
                            gzip.decompress((batch / "response.json.gz").read_bytes())
                        ).hexdigest(),
                        "api_error": response.get("api_error"),
                        "reservation": reservation,
                    }
                )
            else:
                check(sent["payload"] is None, "cpu_no_model_payload", where)
                candidates = sent["cpu_candidates"]
            check(request_files == allowed, "exact_batch_artifacts", where)
            for j, row in enumerate(trials):
                proposed = candidates[j] if j < len(candidates) else None
                check(
                    row["program"] == decoded["slots"][j]["submitted"] == proposed,
                    "raw_proposal_not_repaired",
                    where + f"/{j}",
                )
                check(
                    row["proposal_mode"] == ("initial" if first == 1 else cell["arm"]),
                    "proposal_mode",
                    where,
                )
                if model and response.get("api_error"):
                    check(not row["valid"] and row["stage"] == "API", "api_slots_charged", where)
                regenerated.append(measurement(row, target["rates"], where + f"/{row['slot']}"))
            rows.extend(trials)
        check(rows == complete["trials"], "complete_matches_batches", location)
        metrics = {str(n): prefix(regenerated, n, m["tolerance"]) for n in (16, 64, 128)}
        check(equivalent(metrics, complete["prefixes"]), "independent_prefixes", location)
        cells.append({"cell": cell, "prefixes": metrics})
        all_rows[cell["target"], cell["seed"], cell["arm"]] = regenerated

    actual_requests = {str(p.relative_to(root)) for p in root.rglob("request_started.json.gz")}
    check(actual_requests == expected_request_paths, "no_orphan_archive_requests", "all requests")
    for seed in m["seeds"]:
        initial = [
            [r["program"] for r in rows[:2]] for (t, s, a), rows in all_rows.items() if s == seed
        ]
        check(
            all(v == initial[0] for v in initial),
            "shared_initials_across_targets_and_arms",
            str(seed),
        )
        random_rows = [
            [r["program"] for r in rows]
            for (t, s, a), rows in all_rows.items()
            if s == seed and a == "phase-random"
        ]
        check(
            all(v == random_rows[0] for v in random_rows), "random_target_independence", str(seed)
        )

    smoke_paths = sorted((root / "smoke").glob("*/*/*/complete.json"))
    check(len(smoke_paths) == 1, "one_smoke", "smoke")
    smoke_ids = set()
    for path in smoke_paths:
        smoke = read(path)
        check(
            smoke["cell"] == {"target": "target_0", "seed": 1190, "arm": "phase-random"},
            "smoke_identity",
            str(path.relative_to(root)),
        )
        check(len(smoke["trials"]) == 4, "smoke_budget", "smoke")
        for row in smoke["trials"]:
            measurement(row, targets[0]["rates"], f"smoke/{row['slot']}")
            if row.get("cache_id"):
                smoke_ids.add(row["cache_id"])
    search_ids = {r["cache_id"] for rows in all_rows.values() for r in rows if r.get("cache_id")}
    check(not search_ids & witness_ids, "no_search_witness_cache_overlap", "cache")
    check(not search_ids & smoke_ids, "no_search_smoke_cache_overlap", "cache")
    check(
        {p.name for p in (root / "evaluations").iterdir()} == set(uses),
        "all_evaluations_accounted",
        "evaluations",
    )
    for identifier, entries in uses.items():
        check(
            sum(not e["hit"] for e in entries) == 1, "one_recorded_cache_miss_per_key", identifier
        )
    cache = {
        a: {
            "proposals_with_cache_id": sum(
                bool(r.get("cache_id"))
                for (t, s, arm), rows in all_rows.items()
                if arm == a
                for r in rows
            ),
            "reported_cache_hits": sum(
                r["cache_hit"] for (t, s, arm), rows in all_rows.items() if arm == a for r in rows
            ),
            "unique_keys": len(
                {
                    r["cache_id"]
                    for (t, s, arm), rows in all_rows.items()
                    if arm == a
                    for r in rows
                    if r.get("cache_id")
                }
            ),
        }
        for a in m["arms"]
    }
    lookup = {
        (c["cell"]["target"], c["cell"]["seed"], c["cell"]["arm"]): c["prefixes"]["128"]
        for c in cells
    }
    differences = [
        math.fsum(
            lookup[t["id"], s, "pro-4096"]["auc"] - lookup[t["id"], s, "phase-random"]["auc"]
            for t in targets
        )
        / len(targets)
        for s in m["seeds"]
    ]
    primary = paired(differences)
    published = read(root / "summary.json")
    check(
        equivalent(primary, {k: published["primary"][k] for k in primary}),
        "independent_paired_inference",
        "summary",
    )
    arms = {}
    for a in m["arms"]:
        group = [v for (t, s, arm), v in lookup.items() if arm == a]
        counts = collections.Counter(
            "VALID" if r["valid"] else r["stage"]
            for (t, s, arm), rows in all_rows.items()
            if arm == a
            for r in rows
        )
        arms[a] = {
            "mean_auc": math.fsum(v["auc"] for v in group) / len(group),
            "solves": sum(v["solved"] for v in group),
            "mean_censored_slots": math.fsum(v["evaluations_to_target"] for v in group)
            / len(group),
            "validity": dict(counts),
        }
    check(equivalent(arms, published["arms"]), "independent_arm_metrics", "summary")
    check(equivalent(cells, published["cell_metrics"]), "independent_cell_metrics", "summary")
    secondary = []
    for t in targets:
        for s in m["seeds"]:
            valid = {a: [r for r in all_rows[t["id"], s, a] if r["valid"]] for a in m["arms"]}
            common = min(map(len, valid.values()))
            secondary.append(
                {
                    "target": t["id"],
                    "seed": s,
                    "common_valid_count": common,
                    "best_errors": {
                        a: min(r["loss"] for r in rows[:common]) if common else None
                        for a, rows in valid.items()
                    },
                }
            )
    check(
        equivalent(secondary, published["equal_valid_secondary"]),
        "independent_equal_valid",
        "summary",
    )
    requests.sort(key=lambda r: r["started"])
    balance, peak = 0.0, 0.0
    for i, req in enumerate(requests):
        peak = max(peak, balance + req["reservation"])
        balance += req["known"] + req["reserved"]
        if i:
            check(
                req["started"] >= requests[i - 1]["started"] + requests[i - 1]["duration_s"] - 0.05,
                "serialized_application_calls",
                req["path"],
            )
    costs = {
        "calls": len(requests),
        "known_estimated_usd": math.fsum(r["known"] for r in requests),
        "unknown_usage_reserved_usd": math.fsum(r["reserved"] for r in requests),
        "liability_usd": math.fsum(r["known"] + r["reserved"] for r in requests),
        "input_tokens": sum(r["input"] for r in requests),
        "output_and_thinking_tokens": sum(r["output"] for r in requests),
    }
    old_cost = read(root / "cost_summary.json")
    check(
        equivalent(costs, {k: old_cost[k] for k in costs}),
        "independent_cost_totals",
        "cost_summary",
    )
    check(peak <= m["ceiling_usd"], "liability_cap", "requests")
    for req in requests:
        check(
            req["response_raw_sha256"]
            == old_cost["response_sha256"][req["path"] + "/response.json"],
            "response_digest",
            req["path"],
        )
    for k, v in static_payload.items():
        check(len(v) == 1, "fixed_payload_context", k)
    return {
        "checks": dict(checks),
        "discrepancies": discrepancies,
        "observations": dict(observations),
        "cells": cells,
        "primary": primary,
        "arms": arms,
        "equal_valid_secondary": secondary,
        "qualification": qualification,
        "cache": cache,
        "unique_evaluations": len(uses),
        "costs": costs,
        "peak_with_inflight_reservation_usd": peak,
        "requests": requests,
        "payload_static_sha256": {k: sorted(v) for k, v in static_payload.items()},
        "history_rows_checked": exposed_history,
        "notebook_rows_checked": exposed_notebook,
        "floating_point_tolerance": {"relative": 1e-10, "absolute": 1e-10},
        "conventions": {
            "auc": "trapezoid x=1..128, 127 intervals; invalid prefix 1.0; valid losses not clipped",
            "bootstrap": "10000 Python Random(1300) six-index resamples; order statistics 250 and 9750",
        },
        "inputs": {
            "manifest_sha256": digest(root / "manifest.json"),
            "packing_sha256": digest(repo / "results/nonflat_temporal_v1/evidence.pack.json.gz"),
            "source_archive_sha256": digest(repo / "archive/legacy-source.tar.gz"),
            "protocol_sha256": digest(repo / "docs/ACCOUNTING_AUDIT.md"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.archive, Path.cwd())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(result, indent=2) + "\n").encode()
    with args.out.open("xb") as stream:
        stream.write(gzip.compress(data, mtime=0) if args.out.suffix == ".gz" else data)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "discrepancies",
                    "observations",
                    "primary",
                    "arms",
                    "cache",
                    "costs",
                    "unique_evaluations",
                )
            },
            indent=2,
        )
    )

    if result["discrepancies"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
