"""Complete-panel evidence audit and descriptive grounding metrics."""

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
from analysis.ibex_expressiveness import audit_cell, describe
from analysis.ibex_temporal_v3 import check_feedback
from experiments.ibex_temporal_v3.coverage import descriptor
from experiments.ibex_temporal_v3.program import canonical, interpret
from experiments.ibex_temporal_v3.search import key
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.compiler import assembly
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.notebook import assess


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(l) for l in path.read_text().splitlines()]


def directories(root, manifest):
    return [
        root / "panel" / target / f"seed-{seed}" / policy
        for target, seed, policy in itertools.product(
            manifest["targets"], manifest["seeds"], manifest["policies"]
        )
    ]


def trajectory_summary(selected):
    rounds = collections.defaultdict(collections.Counter)
    roles = collections.defaultdict(collections.Counter)
    for _, trials in selected:
        seen = set()
        for t in trials:
            encoded = json.dumps(t.get("canonical_program"), sort_keys=True)
            if t["slot"] > 2:
                r = rounds[str((t["slot"] - 3) // 2 + 1)]
                role = roles["first" if t["slot"] % 2 else "second"]
                assessment = t["prediction_assessment"]
                for counter in (r, role):
                    counter["requested_slots"] += 1
                    counter["valid"] += t["valid"]
                    counter["duplicate_valid_programs"] += (
                        t["valid"] and encoded in seen
                    )
                    counter["scorable_predictions"] += assessment["scorable"]
                    if assessment["scorable"]:
                        edits = assessment["actual_changes"]
                        counter["one_scalar_leaf_edit"] += (
                            len(edits) == 1
                            and not isinstance(edits[0]["before"], (list, dict))
                            and not isinstance(edits[0]["after"], (list, dict))
                        )
            if t["valid"]:
                seen.add(encoded)
    return {"by_round": dict(rounds), "by_batch_position": dict(roles)}


def describe_panel(manifest, cells):
    result = describe(manifest, cells)
    for policy, report in result["policies"].items():
        selected = [(s, t) for s, t in cells if s["policy"] == policy]
        generated = [t for _, ts in selected for t in ts if t["slot"] > 2]
        reports = [t["prediction_assessment"] for t in generated]
        scorable = [r for r in reports if r["scorable"]]
        report.pop("grid_profiles")
        report.pop("grid_width_transitions_per_edge")
        report["generated_validity"] = dict(
            collections.Counter(
                "VALID" if t["valid"] else t["stage"] for t in generated
            )
        )
        report["mean_behavior_cells_per_run"] = statistics.mean(
            len({descriptor(t["feedback"]) for t in ts if t["valid"]})
            for _, ts in selected
        )
        report["predictions"] = {
            "generated_slots": len(generated),
            "scorable_candidates": len(scorable),
            "unscorable_reasons": dict(
                collections.Counter(r["reason"] for r in reports if not r["scorable"])
            ),
            "matched_bins": sum(r["matched_bins"] for r in scorable),
            "scorable_bins": 8 * len(scorable),
            "always_no_change_matched_bins": sum(
                d == 0 for r in scorable for d in r["observed_directions"]
            ),
            "observed_direction_counts": dict(
                collections.Counter(
                    str(d) for r in scorable for d in r["observed_directions"]
                )
            ),
            "all_directions_supported": sum(
                r["all_directions_supported"] for r in scorable
            ),
            "actual_edit_count_distribution": dict(
                collections.Counter(str(len(r["actual_changes"])) for r in scorable)
            ),
        }
        report["tokens_in"] = sum(t["tokens_in"] for _, ts in selected for t in ts)
        report["tokens_out_including_thinking"] = sum(
            t["tokens_out"] for _, ts in selected for t in ts
        )
        report["trajectory"] = trajectory_summary(selected)
    result["limitations"] = [
        "observed development targets/seeds; no held-out inference",
        "grounding is a package of execution feedback, notebook and instructions",
        "same workload language; descriptor coverage is not intrinsic expressiveness",
        "RTL activity, not gate power",
        "direction agreement is not causal understanding",
        "missing predictions retain their primary proposal cost",
    ]
    return result


def check_execution(execution, feedback):
    if (
        any(execution[k] != feedback[k] for k in ("begin_tick", "end_tick"))
        or len(execution["bins"]) != 8
    ):
        raise ValueError("execution window mismatch")
    for i, b in enumerate(execution["bins"]):
        if (
            any(v < 0 for v in b["retired_by_phase"].values())
            or sum(b["retired_by_phase"].values()) != feedback["retired_per_bin"][i]
        ):
            raise ValueError("phase retirement arithmetic mismatch")
        if (
            b["divide_zero_divisor"] + b["divide_nonzero_divisor"]
            != feedback["retired_classes"][i]["divide"]
        ):
            raise ValueError("divide event arithmetic mismatch")


def check_prerequisites(root, manifest):
    for name, digest in manifest["cpu_gates"].items():
        path = root / "prerequisites" / Path(name).parent.name / "gate.json"
        if file_sha256(path) != digest:
            raise ValueError("CPU gate differs from frozen prerequisite")
        for relative, expected in read(path)["evidence"].items():
            item = path.parent / relative
            if not item.resolve().is_relative_to(path.parent.resolve()):
                raise ValueError("unsafe CPU gate evidence path")
            if file_sha256(item) != expected:
                raise ValueError("CPU gate evidence mismatch")
        if (path.parent / "original/loadable.bin").read_bytes() != (
            path.parent / "annotated/loadable.bin"
        ).read_bytes():
            raise ValueError("CPU instrumentation changed executable")
    gate = root / "prerequisites/ibex_temporal_v4_prediction_gate"
    result = read(gate / "result.json")
    if file_sha256(gate / "result.json") != manifest["prediction_gate_sha256"]:
        raise ValueError("prediction gate differs from frozen prerequisite")
    settings = read(gate / "manifest.json")
    for path, digest in (
        ("schema.json", settings["schema_sha256"]),
        ("inputs/prediction.json", settings["calls"][0]["payload_sha256"]),
    ):
        if file_sha256(gate / path) != digest:
            raise ValueError("prediction gate input mismatch")
    decoded = decode(result["raw_text"], 2, True)
    if (
        decoded != result["decoded"]
        or not result["ready"]
        or result["usage_unknown"]
        or decoded["response_error"] is not None
        or any(
            s["canonical"] is None
            or s["prediction"] is None
            or s["prediction"]["reference_slot"] != 1
            for s in decoded["slots"]
        )
    ):
        raise ValueError("prediction readiness not reproducible")


def audit(root):
    manifest = read(root / "manifest.json")
    check_prerequisites(root, manifest)
    previous = root / "v3_manifest.json"
    if file_sha256(previous) != manifest["previous_manifest_sha256"]:
        raise ValueError("v3 manifest mismatch")
    old = read(previous)
    for name, target in manifest["targets"].items():
        if file_sha256(root / "witnesses" / f"{name}.json") != target["witness_sha256"]:
            raise ValueError("target witness hash mismatch")
        if (
            read(root / "target-evidence" / name / "profile.json")["window_rates"]
            != target["rates"]
        ):
            raise ValueError("target differs from achieved profile")
    for field in ("targets", "scale", "tolerance", "seeds", "budget", "measurement"):
        if old[field] != manifest[field]:
            raise ValueError("changed comparison settings")
    cells, initial, diagnostics = [], {}, collections.Counter()
    for directory in directories(root, manifest):
        summary, trials, batches = (
            read(directory / "summary.json"),
            rows(directory / "trials.jsonl"),
            read(directory / "batches.json"),
        )
        identity = read(directory / "manifest.json")
        if identity["study_sha256"] != file_sha256(root / "manifest.json") or any(
            identity[k] != summary[k] for k in ("target", "seed", "policy")
        ):
            raise ValueError("cell identity mismatch")
        records = {
            t["cache_id"]: read(root / "evaluations" / t["cache_id"] / "result.json")
            for t in trials
            if t["cache_id"]
        }
        audit_cell(manifest, summary, trials, records)
        if directory != (
            root
            / "panel"
            / summary["target"]
            / f"seed-{summary['seed']}"
            / summary["policy"]
        ):
            raise ValueError("cell stored under wrong identity")
        if (
            summary["budget"] != manifest["budget"]
            or summary["valid_slots"] != sum(t["valid"] for t in trials)
            or summary["final_loss"] != trials[-1]["best_loss"]
            or summary["behavior_cells"]
            != len({descriptor(t["feedback"]) for t in trials if t["valid"]})
        ):
            raise ValueError("summary totals mismatch")
        for i, t in enumerate(trials):
            if assess(t, trials[:i], manifest["scale"]) != t["prediction_assessment"]:
                raise ValueError("prediction assessment mismatch")
            if t["cache_id"]:
                p = canonical(t["program"])
                record = records[t["cache_id"]]
                cache = root / "evaluations" / t["cache_id"]
                if (
                    p != t["canonical_program"]
                    or p != read(cache / "program.json")
                    or key(
                        {
                            "program": p,
                            "measurement": manifest["measurement_fingerprint"],
                        }
                    )
                    != t["cache_id"]
                ):
                    raise ValueError("cache program/provenance mismatch")
                if any(
                    t[k] != record.get(k)
                    for k in ("valid", "stage", "feedback", "execution", "allocation")
                ):
                    raise ValueError("trial differs from evaluation record")
                if (cache / "run/program.S").read_text() != assembly(p):
                    raise ValueError("compiled assembly differs from candidate")
                if t["valid"]:
                    functional = read(cache / "run/functional.json")
                    expected = interpret(p)
                    if functional["expected"] != expected:
                        raise ValueError("reference state mismatch")
                    required_inputs = {
                        "Vibex_simple_system": manifest["measurement"]["binary_sha256"],
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
                    for suffix, digest in required_inputs.items():
                        if [
                            v
                            for k, v in functional["inputs"].items()
                            if k.endswith(suffix)
                        ] != [digest]:
                            raise ValueError("evaluation input provenance mismatch")
                    match = re.search(
                        r"AGCWS_STATE ([0-9A-Fa-f ]+)\n",
                        (cache / "run/ibex_simple_system.log").read_text(),
                    )
                    if (
                        not match
                        or [int(x, 16) for x in match[1].split()]
                        != expected["registers"] + expected["memory"]
                    ):
                        raise ValueError("CPU output state mismatch")
                    check_feedback(t["feedback"], record["profile"])
                    check_execution(t["execution"], t["feedback"])
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
                    raise ValueError("statically valid proposal missing evaluation")
        shared = [t["program"] for t in trials[:2]]
        if summary["seed"] in initial and initial[summary["seed"]] != shared:
            raise ValueError("unequal shared initialization")
        initial[summary["seed"]] = shared
        if sum(b["requested_slots"] for b in batches) != manifest["budget"]:
            raise ValueError("batch proposal count mismatch")
        if sum(b["usage_unknown"] for b in batches) != summary["unknown_usage_batches"]:
            raise ValueError("unknown usage mismatch")
        for batch_index, b in enumerate(batches):
            offset = b["first_slot"] - 1
            group = trials[offset : offset + b["requested_slots"]]
            if offset != batch_index * manifest["batch_size"]:
                raise ValueError("noncontiguous batch slots")
            for k in ("tokens_in", "tokens_out"):
                if sum(t[k] for t in group) != b[k]:
                    raise ValueError("batch token allocation mismatch")
            if not math.isclose(
                sum(t["est_cost_usd"] for t in group), b["est_cost_usd"], abs_tol=1e-12
            ):
                raise ValueError("batch cost allocation mismatch")
            if summary["policy"].startswith("agent-") and offset:
                contents = (
                    payload(
                        trials[:offset],
                        {
                            "profile": manifest["targets"][summary["target"]]["rates"],
                            "scale": manifest["scale"],
                            "tolerance": manifest["tolerance"],
                        },
                        len(group),
                        summary["policy"] == "agent-grounded",
                    )
                    + "\n"
                )
                path = directory / f"payload-{offset + 1}.json"
                if (
                    path.read_text() != contents
                    or file_sha256(path) != b["payload_sha256"]
                ):
                    raise ValueError("model payload reconstruction mismatch")
                decoded = decode(b["raw_text"], len(group), True)
                if decoded != b["decoded"]:
                    raise ValueError("raw response decoding mismatch")
                for t, s in zip(group, decoded["slots"]):
                    if (
                        t["program"] != s["submitted"]
                        or t["prediction"] != s["prediction"]
                    ):
                        raise ValueError("model proposal/metadata mismatch")
                    note_error = s["prediction_error"]
                    if s["prediction"] is not None and s["prediction"][
                        "reference_slot"
                    ] not in {p["slot"] for p in trials[:offset] if p["valid"]}:
                        note_error = (
                            "reference was not visible as valid before this batch"
                        )
                    if t["prediction_error"] != note_error:
                        raise ValueError("prediction error/visible reference mismatch")
                diagnostics.update(b.get("finish_reasons", []))
        if summary["policy"] == "random":
            control = rows(
                root / "v3_random" / directory.relative_to(root) / "trials.jsonl"
            )
            if any(
                any(
                    a[k] != b[k]
                    for k in ("program", "valid", "stage", "rates", "loss", "best_loss")
                )
                for a, b in zip(trials, control, strict=True)
            ):
                raise ValueError("random control no longer matches v3")
        cells.append((summary, trials))
    result = describe_panel(manifest, cells)
    result["model_finish_reasons"] = dict(diagnostics)
    return result


def verify(root):
    index = read(root / "sha256.json")
    actual = {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.name != "sha256.json"
    }
    if actual != set(index):
        raise ValueError("archive file inventory differs")
    for name, digest in index.items():
        p = root / name
        if not p.resolve().is_relative_to(root.resolve()) or file_sha256(p) != digest:
            raise ValueError("archive hash/path mismatch")
    manifest = read(root / "manifest.json")
    for name, digest in manifest["sources"].items():
        if file_sha256(root / "sources" / name) != digest:
            raise ValueError("frozen source copy differs")
    if audit(root) != read(root / "aggregate.json"):
        raise ValueError("aggregate arithmetic mismatch")
    return {
        "verified_cells": len(directories(root, manifest)),
        "verified_slots": len(directories(root, manifest)) * manifest["budget"],
        "verified_files": len(index),
        "scope": "compact evidence and arithmetic; not independent simulator/trace re-execution",
    }


def archive(root, destination):
    manifest = read(destination / "manifest.json")
    if any(not (p / "summary.json").exists() for p in directories(root, manifest)):
        raise ValueError("full panel is required for archive")

    def copy(source, relative):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    previous = Path("results/ibex_temporal_v3_development")
    copy(previous / "manifest.json", "v3_manifest.json")
    prerequisites = [Path(p).parent for p in manifest["cpu_gates"]]
    prerequisites.append(Path("results/ibex_temporal_v4_prediction_gate"))
    for directory in prerequisites:
        for p in directory.rglob("*"):
            if p.is_file():
                copy(
                    p, Path("prerequisites") / directory.name / p.relative_to(directory)
                )
    for name in manifest["targets"]:
        copy(
            previous / "witnesses" / f"{name}.json", Path("witnesses") / f"{name}.json"
        )
        for p in (previous / "target-evidence" / name).iterdir():
            if p.is_file():
                copy(p, Path("target-evidence") / name / p.name)
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError("frozen source changed")
        copy(name, Path("sources") / name)
    identifiers = set()
    for p in directories(root, manifest):
        for f in p.glob("*.json*"):
            copy(f, f.relative_to(root))
        identifiers.update(
            t["cache_id"] for t in rows(p / "trials.jsonl") if t["cache_id"]
        )
        if p.name == "random":
            relative = p.relative_to(root) / "trials.jsonl"
            copy(previous / relative, Path("v3_random") / relative)
    for identifier in sorted(identifiers):
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
            f = root / "cache" / identifier / name
            if f.exists():
                copy(f, Path("evaluations") / identifier / name)
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
