"""Audit and summarize a conditional next-batch factorial, not a search matrix."""

import argparse
import collections
import itertools
import json
import math
import re
import shutil
import statistics
from pathlib import Path

import jsonschema

from agcws.provenance import file_sha256
from analysis.ibex_temporal_v3 import check_feedback
from analysis.ibex_temporal_v4 import check_execution
from experiments.ibex_capability_v1.study import (
    ARMS,
    MODEL_ARMS,
    controls,
    estimate,
    read,
    settings,
    summarize_slots,
)
from experiments.ibex_temporal_v3.program import canonical, interpret
from experiments.ibex_temporal_v3.search import error, key
from experiments.ibex_temporal_v4.compiler import assembly
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.notebook import assess


def describe(manifest, cells):
    expected = {(c["context"], c["arm"]) for c in manifest["cells"]}
    actual = {(r["cell"]["context"], r["cell"]["arm"]) for r, _ in cells}
    if actual != expected or len(cells) != len(expected):
        raise ValueError("incomplete/duplicate conditional panel")
    reports = {}
    for arm in ARMS:
        selected = [(r, response) for r, response in cells if r["cell"]["arm"] == arm]
        ts = [t for r, _ in selected for t in r["trials"]]
        if any(len(r["trials"]) != 2 for r, _ in selected):
            raise ValueError("wrong charged slot count")
        predictions = [t["prediction_assessment"] for t in ts]
        scored = [a for a in predictions if a["scorable"]]
        directions = collections.Counter(
            d for a in scored for d in a["observed_directions"]
        )
        report = {
            "contexts": len(selected),
            "requested_slots": len(ts),
            "mean_gain": statistics.mean(r["summary"]["gain"] for r, _ in selected),
            "mean_after_error": statistics.mean(
                r["summary"]["after_error"] for r, _ in selected
            ),
            "improved_contexts": sum(r["summary"]["improved"] for r, _ in selected),
            "already_solved": sum(r["summary"]["already_solved"] for r, _ in selected),
            "newly_solved": sum(r["summary"]["newly_solved"] for r, _ in selected),
            "validity": dict(
                collections.Counter("VALID" if t["valid"] else t["stage"] for t in ts)
            ),
            "predictions": {
                "scorable": len(scored),
                "requested": len(ts),
                "unscorable": dict(
                    collections.Counter(
                        a["reason"] for a in predictions if not a["scorable"]
                    )
                ),
                "matched_bins": sum(a["matched_bins"] for a in scored),
                "scorable_bins": 8 * len(scored),
                "always_neutral_matches": directions[0],
                "largest_observed_class_count": max(directions.values(), default=0),
                "all_eight_supported": sum(
                    a["all_directions_supported"] for a in scored
                ),
            },
            "tokens_in": sum(r["tokens_in"] for _, r in selected),
            "tokens_out_including_thinking": sum(r["tokens_out"] for _, r in selected),
            "thinking_tokens": sum(r.get("thinking_tokens", 0) for _, r in selected),
            "estimated_usd": sum(r["est_cost_usd"] for _, r in selected),
            "unknown_usage": sum(r["usage_unknown"] for _, r in selected),
            "api_errors": sum("exception" in r for _, r in selected),
            "finish_reasons": dict(
                collections.Counter(
                    f for _, r in selected for f in r.get("finish_reasons", [])
                )
            ),
            "model_versions": sorted(
                {r["model_version"] for _, r in selected if r.get("model_version")}
            ),
        }
        s = settings(arm) if arm in MODEL_ARMS else None
        report["unknown_usage_reservation_usd"] = (
            report["unknown_usage"]
            * (200000 * s["input_rate"] + s["max_output_tokens"] * s["output_rate"])
            / 1e6
            if s
            else 0.0
        )
        for field in ("target", "seed"):
            values = sorted({c[field] for c in manifest["contexts"].values()})
            report[f"gain_by_{field}"] = {
                str(value): statistics.mean(
                    r["summary"]["gain"]
                    for r, _ in selected
                    if manifest["contexts"][r["cell"]["context"]][field] == value
                )
                for value in values
            }
        reports[arm] = report
    base = reports["flash-512"]
    candidates = []
    for arm in MODEL_ARMS[1:]:
        r = reports[arm]
        gain_ok = (
            r["mean_gain"] >= 1.1 * base["mean_gain"]
            if base["mean_gain"] > 0
            else r["mean_gain"] > 0
        )
        seeds_better = sum(
            r["gain_by_seed"][s] > base["gain_by_seed"][s] for s in base["gain_by_seed"]
        )
        r["screen"] = {
            "gain_threshold_pass": gain_ok,
            "seed_means_improved": seeds_better,
            "eligible": gain_ok
            and seeds_better >= 2
            and r["validity"].get("VALID", 0) / r["requested_slots"] >= 0.9
            and r["unknown_usage"] == 0
            and r["api_errors"] == 0,
        }
        if r["screen"]["eligible"]:
            candidates.append(arm)
    contrast = lambda a, b: reports[a]["mean_gain"] - reports[b]["mean_gain"]
    return {
        "phase": "fixed-context-development",
        "primary": "mean next-batch best-error reduction; larger is better",
        "arms": reports,
        "paired_gain_contrasts": {
            "reasoning_on_flash": contrast("flash-4096", "flash-512"),
            "reasoning_on_pro": contrast("pro-4096", "pro-512"),
            "model_at_512": contrast("pro-512", "flash-512"),
            "model_at_4096": contrast("pro-4096", "flash-4096"),
            "interaction": contrast("pro-4096", "pro-512")
            - contrast("flash-4096", "flash-512"),
        },
        "screened_candidate": min(
            candidates,
            key=lambda a: (
                reports[a]["mean_after_error"],
                reports[a]["estimated_usd"],
                a,
            ),
        )
        if candidates
        else None,
        "limits": [
            "observed contexts, three reused seed units; no held-out inference",
            "one next batch, not on-policy AUC or cumulative search performance",
            "same language; no intrinsic expressiveness or gate-power claim",
            "thought allowance is not actual reasoning use or causal understanding",
            "screening does not authorize automatic depth or held-out runs",
        ],
    }


def audit(root):
    manifest, old = read(root / "manifest.json"), read(root / "previous_manifest.json")
    if (
        file_sha256(root / "previous_manifest.json")
        != manifest["previous_manifest_sha256"]
    ):
        raise ValueError("prior manifest hash mismatch")
    if manifest["measurement_fingerprint"] != old["measurement_fingerprint"]:
        raise ValueError("measurement fingerprint changed")
    required_cells = set(itertools.product(manifest["contexts"], ARMS))
    if {(c["context"], c["arm"]) for c in manifest["cells"]} != required_cells or len(
        manifest["cells"]
    ) != len(required_cells):
        raise ValueError("declared factorial is incomplete")
    if read(root / "panel_complete.json") != {
        "cells": len(required_cells),
        "slots": 2 * len(required_cells),
    }:
        raise ValueError("completion status mismatch")
    gate = read(root / "endpoint_gate.json")
    expected_gate_paths = [
        f"cells/{c['context']}/{c['arm']}/response.json" for c in manifest["cells"][:4]
    ]
    if (
        gate["response_paths"] != expected_gate_paths
        or not gate["ready"]
        or any(
            read(root / p)["usage_unknown"] or "exception" in read(root / p)
            for p in expected_gate_paths
        )
    ):
        raise ValueError("endpoint acceptance not supported")
    expected_pairs = set(itertools.product(old["targets"], old["seeds"]))
    if {
        (c["target"], c["seed"]) for c in manifest["contexts"].values()
    } != expected_pairs:
        raise ValueError("context selection differs")
    for arm, s in manifest["arms"].items():
        if s != settings(arm):
            raise ValueError("model settings mismatch")
    for name, context in manifest["contexts"].items():
        history = read(root / "contexts" / f"{name}.json")
        parent = root / "parent_histories" / f"{name}.jsonl"
        if file_sha256(parent) != context["parent_history_sha256"]:
            raise ValueError("parent history hash mismatch")
        if history != [json.loads(l) for l in parent.read_text().splitlines()][:6]:
            raise ValueError("context is not declared historical prefix")
        contents = (
            payload(
                history,
                {
                    "profile": old["targets"][context["target"]]["rates"],
                    "scale": old["scale"],
                    "tolerance": old["tolerance"],
                },
                2,
                True,
            )
            + "\n"
        )
        if (root / "payloads" / f"{name}.json").read_text() != contents:
            raise ValueError("payload reconstruction mismatch")
        for folder, field in (
            ("contexts", "history_sha256"),
            ("payloads", "payload_sha256"),
        ):
            if file_sha256(root / folder / f"{name}.json") != context[field]:
                raise ValueError("context hash mismatch")
    cells = []
    for cell in manifest["cells"]:
        directory = root / "cells" / cell["context"] / cell["arm"]
        response, result = (
            read(directory / "response.json"),
            read(directory / "result.json"),
        )
        if result["cell"] != cell or response["cell"] != cell:
            raise ValueError("cell identity mismatch")
        digest = file_sha256(root / "manifest.json")
        if (
            response["manifest_sha256"] != digest
            or read(directory / "request_started.json")["manifest_sha256"] != digest
        ):
            raise ValueError("response provenance mismatch")
        decoded = decode(response["raw_text"], 2, cell["arm"] in MODEL_ARMS)
        if decoded != response["decoded"]:
            raise ValueError("raw response decode mismatch")
        history = read(root / "contexts" / f"{cell['context']}.json")
        if cell["arm"] not in MODEL_ARMS:
            if [s["submitted"] for s in decoded["slots"]] != controls(
                cell["arm"], history, cell["seed"]
            ):
                raise ValueError("CPU control generation mismatch")
        elif not math.isclose(
            response["est_cost_usd"], estimate(response, cell["arm"]), abs_tol=1e-12
        ):
            raise ValueError("pricing arithmetic mismatch")
        target = old["targets"][manifest["contexts"][cell["context"]]["target"]][
            "rates"
        ]
        for index, (t, p) in enumerate(
            zip(result["trials"], decoded["slots"], strict=True), 7
        ):
            if (
                t["slot"] != index
                or t["program"] != p["submitted"]
                or t["prediction"] != p["prediction"]
            ):
                raise ValueError("proposal/slot mismatch")
            note_error = p["prediction_error"]
            if p["prediction"] and p["prediction"]["reference_slot"] not in {
                h["slot"] for h in history if h["valid"]
            }:
                note_error = "reference was not visible as valid before this batch"
            if (
                t["prediction_error"] != note_error
                or assess(t, history, old["scale"]) != t["prediction_assessment"]
            ):
                raise ValueError("prediction outcome mismatch")
            if t["cache_id"]:
                program = canonical(t["program"])
                identifier = key(
                    {
                        "program": program,
                        "measurement": manifest["measurement_fingerprint"],
                    }
                )
                cache = root / "evaluations" / identifier
                record = read(cache / "result.json")
                if (
                    t["cache_id"] != identifier
                    or read(cache / "program.json") != program
                    or t["canonical_program"] != program
                ):
                    raise ValueError("candidate cache mismatch")
                if any(
                    t[k] != record.get(k)
                    for k in ("valid", "stage", "reason", "feedback", "execution")
                ):
                    raise ValueError("trial differs from evaluator")
                if (cache / "run/program.S").read_text() != assembly(program):
                    raise ValueError("assembly mismatch")
                if t["valid"]:
                    f = read(cache / "run/functional.json")
                    expected = interpret(program)
                    if f["expected"] != expected:
                        raise ValueError("reference state mismatch")
                    inputs = {
                        "Vibex_simple_system": old["measurement"]["binary_sha256"],
                        "program.S": file_sha256(cache / "run/program.S"),
                        **{
                            name: manifest["sources"][name]
                            for name in (
                                "experiments/ibex_temporal_v4/evaluate.py",
                                "experiments/ibex_temporal_v4/compiler.py",
                                "experiments/ibex_temporal_v4/events.py",
                                "experiments/ibex_temporal_v3/program.py",
                                "experiments/ibex_temporal_v2/compiler.py",
                            )
                        },
                    }
                    if any(
                        [v for k, v in f["inputs"].items() if k.endswith(suffix)]
                        != [digest]
                        for suffix, digest in inputs.items()
                    ):
                        raise ValueError("CPU/measurement input provenance mismatch")
                    match = re.search(
                        r"AGCWS_STATE ([0-9A-Fa-f ]+)\n",
                        (cache / "run/ibex_simple_system.log").read_text(),
                    )
                    if (
                        not match
                        or [int(x, 16) for x in match[1].split()]
                        != expected["registers"] + expected["memory"]
                    ):
                        raise ValueError("CPU state mismatch")
                    check_feedback(t["feedback"], record["profile"])
                    check_execution(t["execution"], t["feedback"])
                    if t["rates"] != record["profile"][
                        "window_rates"
                    ] or not math.isclose(
                        t["loss"],
                        error(t["rates"], target, old["scale"]),
                        abs_tol=1e-12,
                    ):
                        raise ValueError("target score mismatch")
            else:
                try:
                    canonical(t["program"])
                except jsonschema.ValidationError as exc:
                    if (
                        t["stage"] != "SCHEMA"
                        or t["reason"] != exc.message
                        or t["schema_path"] != list(exc.absolute_path)
                    ):
                        raise ValueError("schema rejection mismatch") from exc
                except ValueError as exc:
                    if t["stage"] != "PROTOCOL" or t["reason"] != str(exc):
                        raise ValueError("protocol rejection mismatch") from exc
                else:
                    raise ValueError("missing valid evaluation")
            if not t["valid"] and (t["rates"] is not None or t["loss"] is not None):
                raise ValueError("invalid workload scored")
        if result["summary"] != summarize_slots(
            history, result["trials"], old["tolerance"]
        ):
            raise ValueError("primary arithmetic mismatch")
        cells.append((result, response))
    return describe(manifest, cells)


def verify(root):
    index = read(root / "sha256.json")
    actual = {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.name != "sha256.json"
    }
    if set(index) != actual:
        raise ValueError("archive file inventory differs")
    for name, digest in index.items():
        path = root / name
        if (
            not path.resolve().is_relative_to(root.resolve())
            or file_sha256(path) != digest
        ):
            raise ValueError("archive file hash/path mismatch")
    manifest = read(root / "manifest.json")
    if file_sha256(root / "schema.json") != manifest["schema_sha256"]:
        raise ValueError("serving schema mismatch")
    for name, digest in manifest["sources"].items():
        if file_sha256(root / "sources" / name) != digest:
            raise ValueError("source snapshot mismatch")
    if audit(root) != read(root / "aggregate.json"):
        raise ValueError("aggregate mismatch")
    return {
        "cells": len(manifest["cells"]),
        "slots": 2 * len(manifest["cells"]),
        "files": len(index),
        "scope": "compact evidence, not independent simulator/trace replay",
    }


def archive(source, destination):
    manifest = read(destination / "manifest.json")

    def copy(path, relative):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

    identifiers = set()
    for cell in manifest["cells"]:
        directory = Path("cells") / cell["context"] / cell["arm"]
        result = read(source / directory / "result.json")
        for p in (source / directory).glob("*.json"):
            copy(p, directory / p.name)
        identifiers.update(t["cache_id"] for t in result["trials"] if t["cache_id"])
    for name, c in manifest["contexts"].items():
        copy(
            Path("results/ibex_temporal_v4_development/panel")
            / c["target"]
            / f"seed-{c['seed']}"
            / "agent-base/trials.jsonl",
            Path("parent_histories") / f"{name}.jsonl",
        )
    for identifier in identifiers:
        for name in (
            "program.json",
            "result.json",
            "driver.log",
            "run/program.S",
            "run/program.json",
            "run/functional.json",
            "run/profile.json",
            "run/feedback.json",
            "run/execution.json",
            "run/phase_map.json",
            "run/ibex_simple_system.log",
            "run/compile.log",
            "run/simulator.log",
        ):
            path = source / "cache" / identifier / name
            if path.exists():
                copy(path, Path("evaluations") / identifier / name)
    for name in ("endpoint_gate.json", "panel_complete.json"):
        copy(source / name, name)
    (destination / "aggregate.json").write_text(
        json.dumps(audit(destination), indent=2) + "\n"
    )
    (destination / "sha256.json").write_text(
        json.dumps(
            {
                str(p.relative_to(destination)): file_sha256(p)
                for p in sorted(destination.rglob("*"))
                if p.is_file() and p.name != "sha256.json"
            },
            indent=2,
        )
        + "\n"
    )
    return verify(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            archive(args.root, args.archive) if args.root else verify(args.archive),
            indent=2,
        )
    )
