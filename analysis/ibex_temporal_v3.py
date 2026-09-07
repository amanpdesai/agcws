"""Complete-panel archive and descriptive factorial analysis; no held-out claims."""

import argparse
import collections
import itertools
import json
import math
import re
import shutil
import statistics
from pathlib import Path

from agcws.provenance import file_sha256
from analysis.ibex_expressiveness import audit_cell, describe
from experiments.ibex_temporal_v3.context import load_context
from experiments.ibex_temporal_v3.coverage import descriptor
from experiments.ibex_temporal_v3.program import allocation, canonical, interpret
from experiments.ibex_temporal_v3.search import key


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def verify_bundle(root, digest):
    if file_sha256(root / "manifest.json") != digest:
        raise ValueError("bundle manifest differs")
    for name, record in read(root / "manifest.json")["files"].items():
        path = root / name
        if (
            not path.resolve().is_relative_to(root.resolve())
            or file_sha256(path) != record["sha256"]
        ):
            raise ValueError("bundle source differs or escapes root")


def panel_cells(root, manifest):
    return [
        root / "panel" / target / f"seed-{seed}" / policy
        for target, seed, policy in itertools.product(
            manifest["targets"], manifest["seeds"], manifest["policies"]
        )
    ]


def describe_panel(manifest, cells):
    result = describe(manifest, cells)
    for policy, report in result["policies"].items():
        selected = [(s, t) for s, t in cells if s["policy"] == policy]
        generated = [
            t
            for _, ts in selected
            for t in ts
            if t["slot"] > manifest["shared_initial_slots"]
        ]
        report.pop("grid_profiles")
        report.pop("grid_width_transitions_per_edge")
        report["mean_behavior_cells_per_run"] = statistics.mean(
            len({descriptor(t["feedback"]) for t in ts if t["valid"]})
            for _, ts in selected
        )
        report["generated_slots"] = len(generated)
        report["generated_validity"] = dict(
            collections.Counter(
                "VALID" if t["valid"] else t["stage"] for t in generated
            )
        )
        report["tokens_in"] = sum(t["tokens_in"] for _, ts in selected for t in ts)
        report["tokens_out_including_thinking"] = sum(
            t["tokens_out"] for _, ts in selected for t in ts
        )
    means = {p: r["mean_auc"] for p, r in result["policies"].items()}
    a, c, f, both = [
        means[p]
        for p in ("agent-base", "agent-context", "agent-correction", "agent-combined")
    ]
    result["descriptive_auc_contrasts"] = {
        "context_without_correction": c - a,
        "context_with_correction": both - f,
        "correction_without_context": f - a,
        "correction_with_context": both - c,
        "interaction": both - c - f + a,
        "interpretation": "negative differences favor the added package; no inferential claim",
    }
    result["limitations"] = [
        "observed development targets and three seeds; no held-out superiority or equivalence",
        "source context is supplied, not autonomous RTL discovery",
        "correction bundles feedback, archive history and an exploration instruction",
        "behavior coverage is per run, not RTL code coverage or intrinsic language expressiveness",
        "fixed-window RTL core activity, not gate-level power",
    ]
    return result


def check_feedback(feedback, profile):
    if any(feedback[k] != profile[k] for k in ("begin_tick", "end_tick")):
        raise ValueError("feedback/activity interval mismatch")
    if feedback["end_tick"] - feedback["begin_tick"] != 400000:
        raise ValueError("wrong feedback duration")
    for counts, total, gaps in zip(
        feedback["retired_classes"],
        feedback["retired_per_bin"],
        feedback["cycles_without_retirement"],
        strict=True,
    ):
        if (
            any(v < 0 for v in counts.values())
            or sum(counts.values()) != total
            or total + gaps != 25000
        ):
            raise ValueError("retirement count arithmetic mismatch")
    descriptor(feedback)


def check_inputs(functional, record_root, manifest):
    expected = {
        "Vibex_simple_system": manifest["measurement"]["binary_sha256"],
        "program.S": file_sha256(record_root / "run/program.S"),
        **{
            name: manifest["sources"][name]
            for name in (
                "experiments/ibex_temporal_v3/program.py",
                "experiments/ibex_temporal_v3/evaluate.py",
                "experiments/ibex_temporal_v3/feedback.py",
                "experiments/ibex_temporal_v2/compiler.py",
            )
        },
    }
    for suffix, digest in expected.items():
        found = [v for k, v in functional["inputs"].items() if k.endswith(suffix)]
        if found != [digest]:
            raise ValueError(f"evaluation input provenance mismatch: {suffix}")


def audit(root):
    manifest = read(root / "manifest.json")
    previous_path = root / "v2_manifest.json"
    if file_sha256(previous_path) != manifest["v2_manifest_sha256"]:
        raise ValueError("v2 reference manifest mismatch")
    previous = read(previous_path)
    for field in ("targets", "scale", "tolerance", "measurement", "seeds", "budget"):
        if previous[field] != manifest[field]:
            raise ValueError(f"v2 comparison setting changed: {field}")
    for name, target in manifest["targets"].items():
        if file_sha256(root / "witnesses" / f"{name}.json") != target["witness_sha256"]:
            raise ValueError("target witness hash differs")
        if (
            read(root / "target-evidence" / name / "profile.json")["window_rates"]
            != target["rates"]
        ):
            raise ValueError("target differs from achieved profile")
    cells, initial = [], {}
    verify_bundle(root / "context_bundle", manifest["context_sha256"])
    source_payload = load_context(root / "context_bundle", manifest["context_sha256"])
    if key(source_payload) != manifest["context_payload_sha256"]:
        raise ValueError("source treatment payload mismatch")
    for directory in panel_cells(root, manifest):
        summary, trials = (
            read(directory / "summary.json"),
            rows(directory / "trials.jsonl"),
        )
        run = read(directory / "manifest.json")
        if run["study_sha256"] != file_sha256(root / "manifest.json"):
            raise ValueError("mixed study manifests")
        policy, seed = summary["policy"], summary["seed"]
        if (run["target"], run["policy"], run["seed"]) != (
            summary["target"],
            policy,
            seed,
        ):
            raise ValueError("cell identity mismatch")
        records = {
            t["cache_id"]: read(root / "evaluations" / t["cache_id"] / "result.json")
            for t in trials
            if t["cache_id"]
        }
        audit_cell(manifest, summary, trials, records)
        if summary["budget"] != manifest["budget"] or summary["valid_slots"] != sum(
            t["valid"] for t in trials
        ):
            raise ValueError("summary proposal/validity count mismatch")
        if summary["final_loss"] != trials[-1]["best_loss"]:
            raise ValueError("summary final loss mismatch")
        for t in trials:
            if t["prompt_sha256"] != manifest["prompts"][policy]:
                raise ValueError("wrong treatment prompt")
            if t["cache_id"]:
                record_root = root / "evaluations" / t["cache_id"]
                program = canonical(t["program"])
                if program != t["canonical_program"] or program != read(
                    record_root / "program.json"
                ):
                    raise ValueError("canonical program mismatch")
                if (
                    key(
                        {
                            "program": program,
                            "measurement": manifest["measurement_fingerprint"],
                        }
                    )
                    != t["cache_id"]
                ):
                    raise ValueError("cache provenance mismatch")
                record = records[t["cache_id"]]
                if any(
                    t[k] != record.get(k)
                    for k in ("valid", "stage", "feedback", "allocation")
                ):
                    raise ValueError("trial differs from evaluation")
                if t["allocation"] != allocation(program):
                    raise ValueError("wrong operation allocation")
                if t["valid"]:
                    functional = read(record_root / "run/functional.json")
                    check_inputs(functional, record_root, manifest)
                    if functional["expected"] != interpret(program):
                        raise ValueError("architectural reference mismatch")
                    match = re.search(
                        r"AGCWS_STATE ([0-9A-Fa-f ]+)\n",
                        (record_root / "run/ibex_simple_system.log").read_text(),
                    )
                    expected = functional["expected"]
                    if (
                        not match
                        or [int(v, 16) for v in match[1].split()]
                        != expected["registers"] + expected["memory"]
                    ):
                        raise ValueError("CPU state evidence mismatch")
                    check_feedback(t["feedback"], record["profile"])
            reference = next(
                (p for p in trials if p["slot"] == t["reference_slot"]), None
            )
            delta = (
                [x - y for x, y in zip(t["rates"], reference["rates"])]
                if t["valid"] and reference
                else None
            )
            if reference and (reference["slot"] >= t["slot"] or not reference["valid"]):
                raise ValueError("invalid feedback reference")
            if delta != t["rate_delta_from_reference"]:
                raise ValueError("reference delta mismatch")
        shared = [t["program"] for t in trials[: manifest["shared_initial_slots"]]]
        if seed in initial and initial[seed] != shared:
            raise ValueError("shared initialization differs")
        initial[seed] = shared
        coverage = len({descriptor(t["feedback"]) for t in trials if t["valid"]})
        if coverage != summary["behavior_cells"]:
            raise ValueError("behavior coverage mismatch")
        batches = read(directory / "batches.json")
        if sum(b["requested_slots"] for b in batches) != manifest["budget"]:
            raise ValueError("proposal accounting mismatch")
        if sum(b["usage_unknown"] for b in batches) != summary["unknown_usage_batches"]:
            raise ValueError("unknown usage accounting mismatch")
        for field in ("tokens_in", "tokens_out"):
            if sum(t[field] for t in trials) != sum(b[field] for b in batches):
                raise ValueError("token accounting mismatch")
        if not math.isclose(
            sum(b["est_cost_usd"] for b in batches),
            summary["est_cost_usd"],
            abs_tol=1e-12,
        ):
            raise ValueError("cost accounting mismatch")
        source_path = directory / "source_context.json"
        if policy in ("agent-context", "agent-combined"):
            if read(source_path) != source_payload:
                raise ValueError("source arm did not record frozen context")
        elif source_path.exists():
            raise ValueError("source context leaked into control arm")
        if policy == "random":
            old = rows(
                root / "v2_random" / directory.relative_to(root) / "trials.jsonl"
            )
            if len(old) != len(trials) or any(
                any(
                    a[k] != b[k]
                    for k in ("program", "valid", "stage", "rates", "loss", "best_loss")
                )
                for a, b in zip(old, trials)
            ):
                raise ValueError("random control no longer reproduces v2")
        cells.append((summary, trials))
    return describe_panel(manifest, cells)


def archive(root, destination):
    manifest = read(destination / "manifest.json")
    previous = Path("results/ibex_proposal_v2_development")
    shutil.copy2(previous / "manifest.json", destination / "v2_manifest.json")
    (destination / "witnesses").mkdir(exist_ok=True)
    for name in manifest["targets"]:
        shutil.copy2(previous / "witnesses" / f"{name}.json", destination / "witnesses")
        shutil.copytree(
            previous / "gate-evidence" / name,
            destination / "target-evidence" / name,
            dirs_exist_ok=True,
        )
        for seed in manifest["seeds"]:
            relative = Path("panel") / name / f"seed-{seed}" / "random/trials.jsonl"
            target = destination / "v2_random" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(previous / relative, target)
    for directory in panel_cells(root, manifest):
        target = destination / directory.relative_to(root)
        target.mkdir(parents=True, exist_ok=True)
        for name in (
            "summary.json",
            "trials.jsonl",
            "batches.json",
            "manifest.json",
            "source_context.json",
        ):
            if (directory / name).exists():
                shutil.copy2(directory / name, target / name)
        if not (directory / "summary.json").exists():
            raise ValueError("cannot archive incomplete panel")
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"frozen source changed: {name}")
        target = destination / "sources" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(name, target)
    verify_bundle(Path(manifest["context_root"]), manifest["context_sha256"])
    bundle = destination / "context_bundle"
    if bundle.exists():
        verify_bundle(bundle, manifest["context_sha256"])
    else:
        shutil.copytree(manifest["context_root"], bundle)
    # Keep the third-party license with the copied source, outside the agent bundle.
    shutil.copy2("third_party/ibex/LICENSE", destination / "RTL_LICENSE")
    identifiers = {
        t["cache_id"]
        for directory in panel_cells(root, manifest)
        for t in rows(directory / "trials.jsonl")
        if t["cache_id"]
    }
    for identifier in sorted(identifiers):
        source, target = (
            root / "cache" / identifier,
            destination / "evaluations" / identifier,
        )
        for name in (
            "program.json",
            "result.json",
            "driver.log",
            "run/functional.json",
            "run/profile.json",
            "run/feedback.json",
            "run/program.S",
            "run/ibex_simple_system.log",
            "run/compile.log",
            "run/simulator.log",
        ):
            if (source / name).exists():
                (target / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / name, target / name)
    result = audit(destination)
    (destination / "aggregate.json").write_text(json.dumps(result, indent=2) + "\n")
    index = {
        str(p.relative_to(destination)): file_sha256(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file() and p.name != "sha256.json"
    }
    (destination / "sha256.json").write_text(json.dumps(index, indent=2) + "\n")
    return verify(destination)


def verify(root):
    index = read(root / "sha256.json")
    for name, digest in index.items():
        path = root / name
        if (
            not path.resolve().is_relative_to(root.resolve())
            or file_sha256(path) != digest
        ):
            raise ValueError(f"archive hash/path mismatch: {name}")
    manifest = read(root / "manifest.json")
    for name, digest in manifest["sources"].items():
        if file_sha256(root / "sources" / name) != digest:
            raise ValueError("frozen source copy differs")
    if file_sha256(root / "gate.json") != manifest["gate_sha256"]:
        raise ValueError("numeric gate mismatch")
    result = audit(root)
    if result != read(root / "aggregate.json"):
        raise ValueError("aggregate arithmetic mismatch")
    return {
        "verified_cells": len(panel_cells(root, manifest)),
        "verified_slots": len(panel_cells(root, manifest)) * manifest["budget"],
        "verified_files": len(index),
        "scope": "compact evidence/provenance/arithmetic audit, not a simulator rerun",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify(args.archive), indent=2))
    elif args.root:
        print(json.dumps(archive(args.root, args.archive), indent=2))
    else:
        parser.error("--root is required for archival")
