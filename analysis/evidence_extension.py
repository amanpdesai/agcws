"""Secondary analyses and readable examples from archived measurements; never runs tools."""

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from analysis.accounting_audit import equivalent, read
from analysis.accounting_math import prefix, rms


def coverage(rows, calibration):
    lo, hi = calibration["p_min"], calibration["p_max"]
    epsilon = calibration["epsilon_scalar"]
    if not all(math.isfinite(x) for x in (lo, hi, epsilon)) or hi <= lo or epsilon <= 0:
        raise ValueError("finite nondegenerate envelope and positive tolerance required")
    valid = [r for r in rows if r["valid"]]
    if any(r["useful_work"] < calibration["useful_work_floor"] for r in valid):
        raise ValueError("valid corpus contains sub-floor work")
    values = [(r["activity"] - lo) / (hi - lo) for r in valid]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("nonfinite activity")
    centers = [(i + 0.5) / 10 for i in range(10)]
    hits = [[r["index"] for r, q in zip(valid, values) if abs(q - c) <= epsilon] for c in centers]
    occupied = sorted({min(9, int(q * 10)) for q in values if 0 <= q <= 1})
    return {
        "rule": "ten bin centers 0.05..0.95; hit iff |q-center| <= frozen epsilon; no clipping",
        "epsilon": epsilon,
        "p_min": lo,
        "p_max": hi,
        "valid_records": len(valid),
        "total_records": len(rows),
        "centers": centers,
        "hit_indices": hits,
        "coverage": sum(bool(h) for h in hits) / 10,
        "occupancy_secondary": len(occupied) / 10,
        "occupied_bins": occupied,
        "out_of_envelope_indices": [r["index"] for r, q in zip(valid, values) if not 0 <= q <= 1],
    }


def costs(requests, solves, cells):
    known = math.fsum(r["known"] for r in requests)
    reserved = math.fsum(r["reserved"] for r in requests)
    return {
        "known_estimated_usd": known,
        "unknown_reserved_usd": reserved,
        "liability_usd": known + reserved,
        "cells": cells,
        "solves": solves,
        "known_usd_per_run": known / cells,
        "known_usd_per_solved_cell": known / solves if solves else None,
        "liability_usd_per_solved_cell": (known + reserved) / solves if solves else None,
        "model_request_wall_s": math.fsum(r["duration_s"] for r in requests),
        "compute_cost_usd": None,
    }


def build(repo, archive):
    inputs = {}

    def load(path):
        # Archive-relative paths survive extraction into a different directory.
        name = (
            "results/nonflat_temporal_v1/" + str(path.relative_to(archive))
            if path.is_relative_to(archive)
            else str(path.relative_to(repo))
        )
        inputs[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return read(path)

    audit = load(repo / "results/accounting_audit_v1/reconstruction.json.gz")
    if audit["discrepancies"]:
        raise ValueError("accounting audit has unresolved discrepancies")
    manifest = load(archive / "manifest.json")
    targets = load(archive / "targets.json")
    published = load(archive / "summary.json")
    cells, examples, candidates = [], {}, {}
    for target in targets:
        for seed in manifest["seeds"]:
            for arm in manifest["arms"]:
                location = f"panel/{target['id']}/{seed}/{arm}"
                complete = load(archive / location / "complete.json")
                rows = complete["trials"]
                for row in rows:
                    if row["valid"]:
                        if not equivalent(
                            rms(row["rates"], target["rates"], manifest["scale"]), row["loss"]
                        ):
                            raise ValueError("archived rates/loss mismatch")
                        candidates.setdefault(row["cache_id"], row)
                metrics = {}
                for n in (16, 32, 64, 128):
                    metric = prefix(rows, n, manifest["tolerance"])
                    if str(n) in complete["prefixes"] and not equivalent(
                        metric, complete["prefixes"][str(n)]
                    ):
                        raise ValueError("frozen prefix differs")
                    metrics[str(n)] = {k: v for k, v in metric.items() if k != "curve"}
                requests = [r for r in audit["requests"] if r["path"].startswith(location + "/")]
                cells.append(
                    {
                        "cell": complete["cell"],
                        "prefixes": metrics,
                        "cost": costs(requests, int(metrics["128"]["solved"]), 1),
                    }
                )
    budgets = {}
    for n in (16, 32, 64, 128):
        arms = {}
        for arm in manifest["arms"]:
            selected = [c for c in cells if c["cell"]["arm"] == arm]
            measures = [c["prefixes"][str(n)] for c in selected]
            requests = [
                r
                for r in audit["requests"]
                if r["path"].split("/")[3] == arm and int(r["path"].split("/")[-1]) + 1 <= n
            ]
            arms[arm] = {
                "mean_auc": statistics.mean(m["auc"] for m in measures),
                "mean_auc_per_interval": statistics.mean(m["mean_auc"] for m in measures),
                "mean_final_error": statistics.mean(m["final_loss"] for m in measures),
                "solves": sum(m["solved"] for m in measures),
                "cells": len(measures),
                "mean_censored_slots": statistics.mean(
                    m["evaluations_to_target"] for m in measures
                ),
                "cost": costs(requests, sum(m["solved"] for m in measures), len(measures)),
            }
        deltas = []
        for seed in manifest["seeds"]:
            means = {
                arm: statistics.mean(
                    c["prefixes"][str(n)]["auc"]
                    for c in cells
                    if c["cell"]["arm"] == arm and c["cell"]["seed"] == seed
                )
                for arm in manifest["arms"]
            }
            deltas.append(means["pro-4096"] - means["phase-random"])
        budgets[str(n)] = {
            "arms": arms,
            "pro_minus_random_seed_deltas": deltas,
            "mean_difference": statistics.mean(deltas),
        }
    for arm in manifest["arms"]:
        if not equivalent(
            budgets["128"]["arms"][arm]["mean_auc"], published["arms"][arm]["mean_auc"]
        ):
            raise ValueError("full-budget headline differs")

    scalar = {}
    for design, directory in [
        ("aes", "aes_transactions_calibration"),
        ("axi_dma", "dma_pipelined_calibration"),
    ]:
        base = repo / "results" / directory
        calibration = load(base / "calibration.json")
        source = base / "corpus.jsonl"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != calibration["corpus_sha256"]:
            raise ValueError("frozen calibration corpus hash differs")
        inputs[str(source.relative_to(repo))] = digest
        corpus = [json.loads(line) for line in source.read_text().splitlines()]
        scalar[design] = {"calibration": calibration, **coverage(corpus, calibration)}
        for label, q in (("low", 0.0), ("mid", 0.5), ("high", 1.0)):
            value = calibration["p_min"] + q * (calibration["p_max"] - calibration["p_min"])
            selected = min(
                (r for r in corpus if r["valid"]),
                key=lambda r: (abs(r["activity"] - value), r["index"]),
            )
            examples[f"{design}_{label}"] = {
                "design": design,
                "label": label,
                "fidelity": "RTL activity, not watts",
                "selection": "nearest frozen envelope q=0/0.5/1; ties by corpus index; not a tolerance solve",
                "source": str(source.relative_to(repo)),
                "source_index": selected["index"],
                "calibration": calibration,
                "record": selected,
            }
    temporal = load(repo / "results/aes_transactions_temporal_check.json")
    for case in temporal["cases"]:
        if case["name"] in ("burst_then_idle", "ramp"):
            examples["aes_" + case["name"]] = {
                "design": "aes",
                "label": case["name"],
                "fidelity": "RTL activity, not watts",
                "selection": "existing named capability-check case; not selected for fit",
                "source": "results/aes_transactions_temporal_check.json",
                "record": case,
                "window": temporal["window"],
                "validity_scope": "archived functional-reference capability check; not held-out search",
            }
    gate = load(repo / "results/windowed_power_v1/validation.json")
    for case in gate["cases"]:
        if case["policy"] != "random":
            continue
        base = (
            repo / "results/structural_temporal_finalist_validation_v1/replays" / case["replay_id"]
        )
        examples[f"{case['design']}_temporal_{case['target']}"] = {
            "design": case["design"],
            "label": "temporal_" + case["target"],
            "selection": "all predeclared random-policy finalists; not selected for gate fit",
            "fidelity": "archived zero-delay GLS windowed dynamic power; not signoff power",
            "source": "results/windowed_power_v1/validation.json",
            "profile": case,
            "workload": load(base / "workload.json"),
            "validation": load(base / "completed.json"),
            "provenance": load(base / "gls_provenance.json"),
        }
    ordered = sorted(candidates, key=lambda k: (statistics.mean(candidates[k]["rates"]), k))
    for label, identifier in zip(
        ("low", "mid", "high"), (ordered[0], ordered[(len(ordered) - 1) // 2], ordered[-1])
    ):
        base = archive / "evaluations" / identifier
        record = load(base / "result.json.gz")
        program = load(base / "program.json.gz")
        if (
            not record["valid"]
            or record["profile"]["window_rates"] != candidates[identifier]["rates"]
        ):
            raise ValueError("selected example disagrees with evaluation")
        examples["ibex_" + label] = {
            "design": "ibex",
            "label": label,
            "fidelity": "RTL activity, not watts",
            "selection": "min/lower-median/max mean rate among unique valid confirmation programs; ties by cache ID",
            "scope": "descriptive observed levels, not a calibrated scalar envelope or target solve",
            "source": "results/nonflat_temporal_v1/evaluations/" + identifier,
            "program": program,
            "profile": record["profile"],
            "valid": record["valid"],
            "allocation": record["allocation"],
            "measurement_fingerprint": manifest["measurement_fingerprint"],
        }
    return {
        "scope": "post-hoc existing-evidence analysis; no new measurement or causal claim",
        "budget_convention": "trapezoidal x=1..N; invalid-prefix value 1; six paired seeds; descriptive prefixes",
        "cost_convention": "all consumed batch calls through prefix, including failed/unsolved cells and post-solve calls; estimates not invoices",
        "budgets": budgets,
        "cells": cells,
        "scalar_coverage": scalar,
        "external_checks": {
            "actual_credit_balance": "unverified",
            "provider_invoice": "unverified",
            "organizer_access_and_limits": "unverified",
        },
        "missing_categories": {
            "ibex_scalar_coverage": "no frozen scalar corpus selected for the current temporal backend",
            "ibex_burst_ramp": "not assigned: confirmation targets were not qualified as these analytic families",
            "axi_dma_burst_ramp": "not extracted in this slice; requires a provenance-complete temporal case selection",
        },
        "inputs_sha256": inputs,
        "analysis_source_sha256": {
            name: hashlib.sha256((repo / name).read_bytes()).hexdigest()
            for name in (
                "analysis/evidence_extension.py",
                "analysis/accounting_math.py",
                "analysis/accounting_audit.py",
            )
        },
    }, examples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--verify", action="store_true", help="compare existing artifacts without writing"
    )
    args = parser.parse_args()
    report, examples = build(Path.cwd().resolve(), args.archive.resolve())
    if args.verify:
        if read(args.out / "analysis.json") != report:
            raise ValueError("secondary report differs")
        actual = {p.stem: read(p) for p in (args.out / "workloads").glob("*.json")}
        if actual != examples:
            raise ValueError("readable suite differs")
        print("Secondary report and readable suite reproduced exactly")
        return
    args.out.mkdir(parents=True, exist_ok=False)
    suite = args.out / "workloads"
    suite.mkdir()
    for name, value in sorted(examples.items()):
        (suite / (name + ".json")).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    (args.out / "analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
