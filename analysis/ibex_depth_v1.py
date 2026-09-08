"""Independent compact-evidence checks and descriptive depth-panel analysis."""

import argparse
import collections
import gzip
import hashlib
import itertools
import json
import math
import random
import re
import shutil
import statistics
from pathlib import Path

import jsonschema

from agcws.provenance import file_sha256
from analysis.ibex_temporal_v3 import check_feedback
from analysis.ibex_temporal_v4 import check_execution
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.model import ARMS, MODELS, cost, settings
from experiments.ibex_depth_v1.storage import read
from experiments.ibex_depth_v1.study import controls
from experiments.ibex_temporal_v3.coverage import BehaviorArchive
from experiments.ibex_temporal_v3.program import canonical, interpret, random_program
from experiments.ibex_temporal_v3.search import error, key
from experiments.ibex_temporal_v4.compiler import assembly
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.notebook import assess


def text(root, name):
    path = root / name
    if path.exists():
        return path.read_text()
    return gzip.decompress(Path(str(path) + ".gz").read_bytes()).decode()


def value(root, name):
    return json.loads(text(root, name))


def check_trial(root, t, manifest):
    if not t["valid"] and (t["loss"] is not None or t["rates"] is not None):
        raise ValueError("invalid candidate was scored")
    identifier = t["cache_id"]
    if identifier is None:
        if t["stage"] == "API":
            if t["program"] is not None:
                raise ValueError("API failure has a fabricated program")
            return
        try:
            canonical(t["program"])
        except jsonschema.ValidationError as exc:
            if t["stage"] != "SCHEMA" or t["reason"] != exc.message:
                raise ValueError("schema rejection differs") from exc
        except ValueError as exc:
            if t["stage"] != "PROTOCOL" or t["reason"] != str(exc):
                raise ValueError("protocol rejection differs") from exc
        else:
            raise ValueError("valid program has no evaluation")
        return
    p = canonical(t["program"])
    if identifier != key(
        {"program": p, "measurement": manifest["measurement_fingerprint"]}
    ):
        raise ValueError("cache identity differs")
    directory = f"evaluations/{identifier}"
    record = value(root, f"{directory}/result.json")
    if value(root, f"{directory}/program.json") != p or t["canonical_program"] != p:
        raise ValueError("cached program differs")
    for k in ("valid", "stage", "reason", "allocation", "execution", "feedback"):
        if t[k] != record.get(k):
            raise ValueError(f"cached {k} differs")
    if text(root, f"{directory}/run/program.S") != assembly(p):
        raise ValueError("compiled assembly differs")
    if not t["valid"]:
        diagnostic = text(root, f"{directory}/driver.log")
        required = {
            "USEFUL_WORK": "useful work or observation window did not complete in time",
            "FUNCTIONAL": "architectural reference mismatch",
        }[t["stage"]]
        if required not in diagnostic:
            raise ValueError("failure evidence missing")
        return
    expected = interpret(p)
    functional = value(root, f"{directory}/run/functional.json")
    if functional["expected"] != expected or not functional["functional_ok"]:
        raise ValueError("functional reference differs")
    parent = read(root / "parent_manifest.json")
    inputs = {
        "Vibex_simple_system": parent["measurement"]["binary_sha256"],
        "program.S": hashlib.sha256(
            text(root, f"{directory}/run/program.S").encode()
        ).hexdigest(),
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
        [v for k, v in functional["inputs"].items() if k.endswith(suffix)] != [digest]
        for suffix, digest in inputs.items()
    ):
        raise ValueError("CPU/evaluator source provenance differs")
    match = re.search(
        r"AGCWS_STATE ([0-9A-Fa-f ]+)\n",
        text(root, f"{directory}/run/ibex_simple_system.log"),
    )
    if (
        not match
        or [int(x, 16) for x in match[1].split()]
        != expected["registers"] + expected["memory"]
    ):
        raise ValueError("CPU state differs")
    profile = record["profile"]
    check_feedback(t["feedback"], profile)
    check_execution(t["execution"], t["feedback"])
    if profile["clock_edges"] != 200000 or profile["window_rates"] != [
        v / 25000 for v in profile["window_bit_transitions"]
    ]:
        raise ValueError("rate/window arithmetic differs")
    if t["rates"] != profile["window_rates"]:
        raise ValueError("trial rates differ")


def describe(manifest, histories, responses):
    expected = {(c["target"], c["seed"], c["arm"]) for c in manifest["cells"]}
    if set(histories) != expected:
        raise ValueError("incomplete or duplicate panel")
    result = {"phase": "development-only", "prefixes": {}, "cost": {}}
    for budget in manifest["prefixes"]:
        prefix = {}
        reports = {
            k: summarize(h, budget, manifest["tolerance"]) for k, h in histories.items()
        }
        for arm in ARMS:
            selected = [(k, r) for k, r in reports.items() if k[2] == arm]
            trials = [
                t for k, h in histories.items() if k[2] == arm for t in h[:budget]
            ]
            predictions = [
                t["prediction_assessment"]
                for t in trials
                if t["proposal_mode"] != "initial"
            ]
            scorable = [p for p in predictions if p["scorable"]]
            prefix[arm] = {
                "cells": len(selected),
                "slots": len(trials),
                "mean_auc": statistics.mean(r["auc"] for _, r in selected),
                "mean_normalized_auc": statistics.mean(
                    r["mean_auc"] for _, r in selected
                ),
                "solve_count": sum(r["solved"] for _, r in selected),
                "mean_censored_evaluations": statistics.mean(
                    r["evaluations_to_target"] for _, r in selected
                ),
                "validity": dict(
                    collections.Counter(
                        "VALID" if t["valid"] else t["stage"] for t in trials
                    )
                ),
                "unique_programs": len(
                    {t["cache_id"] for t in trials if t["cache_id"]}
                ),
                "prediction_scorable": len(scorable),
                "prediction_correct_bins": sum(p["matched_bins"] for p in scorable),
                "prediction_bins": 8 * len(scorable),
                "auc_by_seed": {
                    str(s): statistics.mean(r["auc"] for k, r in selected if k[1] == s)
                    for s in manifest["seeds"]
                },
                "auc_by_target": {
                    t: statistics.mean(r["auc"] for k, r in selected if k[0] == t)
                    for t in manifest["targets"]
                },
            }
        contrasts = {}
        for arm in ("pro-4096", "flash-4096", "coverage"):
            contrasts[f"{arm}-minus-random"] = {
                str(seed): prefix[arm]["auc_by_seed"][str(seed)]
                - prefix["random"]["auc_by_seed"][str(seed)]
                for seed in manifest["seeds"]
            }
        equal = []
        for target, seed in itertools.product(manifest["targets"], manifest["seeds"]):
            valid = {
                arm: [
                    t["loss"]
                    for t in histories[target, seed, arm][:budget]
                    if t["valid"]
                ]
                for arm in ARMS
            }
            count = min(map(len, valid.values()))
            row = {
                "target": target,
                "seed": seed,
                "matched_valid_count": count,
                "mean_best_error": {},
            }
            for arm, losses in valid.items():
                curve = [min(losses[: i + 1]) for i in range(count)]
                row["mean_best_error"][arm] = statistics.mean(curve) if count else None
            equal.append(row)
        result["prefixes"][str(budget)] = {
            "arms": prefix,
            "paired_seed_auc_differences": contrasts,
            "equal_valid_secondary": equal,
        }
    for arm in MODELS:
        selected = [r for a, r in responses if a == arm]
        result["cost"][arm] = {
            "calls": len(selected),
            "known_estimated_usd": sum(
                r["estimated_usd"] for r in selected if not r["usage_unknown"]
            ),
            "unknown_usage_calls": sum(r["usage_unknown"] for r in selected),
            "api_failures": sum(bool(r.get("api_error")) for r in selected),
            "known_tokens_in": sum(
                r["tokens_in"] for r in selected if not r["usage_unknown"]
            ),
            "known_tokens_out": sum(
                r["tokens_out"] for r in selected if not r["usage_unknown"]
            ),
            "finish_reasons": dict(
                collections.Counter(f for r in selected for f in r["finish_reasons"])
            ),
        }
    result["limits"] = (
        "Three development seeds, dependent prefixes; descriptive, not held-out inference or power superiority."
    )
    return result


def audit(root):
    manifest = read(root / "manifest.json")
    if read(root / "parent_manifest.json")["targets"] != manifest["targets"]:
        raise ValueError("target corpus differs from parent")
    if file_sha256(root / "parent_manifest.json") != manifest["parent_sha256"]:
        raise ValueError("parent fingerprint differs")
    if file_sha256(root / "schema.json") != manifest["schema_sha256"]:
        raise ValueError("schema fingerprint differs")
    if manifest["models"] != {arm: settings(arm) for arm in MODELS}:
        raise ValueError("model settings differ")
    histories, responses = {}, []
    digest = file_sha256(root / "manifest.json")
    for cell in manifest["cells"]:
        target, seed, arm = cell["target"], cell["seed"], cell["arm"]
        directory = f"panel/{target}/{seed}/{arm}"
        if value(root, f"{directory}/identity.json") != {
            "cell": cell,
            "manifest_sha256": digest,
        }:
            raise ValueError("cell identity differs")
        rng, archive, history = random.Random(seed), BehaviorArchive(), []
        for offset in range(0, max(manifest["prefixes"]), 2):
            batch = f"{directory}/batches/{offset + 1:03d}"
            model_batch = arm in MODELS and offset > 0
            candidates = (
                [random_program(rng) for _ in range(2)] if offset == 0 else None
            )
            if offset and not model_batch:
                candidates = controls(arm, rng, archive)
            contents = (
                payload(
                    history,
                    {
                        "profile": manifest["targets"][target]["rates"],
                        "scale": manifest["scale"],
                        "tolerance": manifest["tolerance"],
                    },
                    2,
                    True,
                )
                if model_batch
                else None
            )
            identity = {
                "cell": cell,
                "first_slot": offset + 1,
                "manifest_sha256": digest,
            }
            if value(root, f"{batch}/input.json") != {
                "identity": identity,
                "payload": contents,
                "cpu_candidates": candidates,
            }:
                raise ValueError("payload/control reconstruction differs")
            if model_batch:
                response = value(root, f"{batch}/response.json")
                start = value(root, f"{batch}/request_started.json")
                if response["identity"] != identity or start["identity"] != identity:
                    raise ValueError("request identity differs")
                if start["reservation_usd"] != cost(
                    arm, 200000, settings(arm)["max_output_tokens"]
                ):
                    raise ValueError("request reservation differs")
                if response.get("api_error"):
                    if response["raw_text"] or not response["usage_unknown"]:
                        raise ValueError("API failure has fabricated output or usage")
                elif response["model_version"] != manifest["models"][arm]["model"]:
                    raise ValueError("reported model differs")
                if not response["usage_unknown"]:
                    fields = response["usage_fields"]
                    if (
                        response["tokens_in"] != fields["prompt_token_count"]
                        or response["tokens_out"]
                        != fields["candidates_token_count"]
                        + fields["thoughts_token_count"]
                    ):
                        raise ValueError("usage decomposition differs")
                elif response["estimated_usd"] is not None:
                    raise ValueError("unknown usage presented as known cost")
                if not response["usage_unknown"] and not math.isclose(
                    response["estimated_usd"],
                    cost(arm, response["tokens_in"], response["tokens_out"]),
                    abs_tol=1e-12,
                ):
                    raise ValueError("cost differs")
                responses.append((arm, response))
                decoded = decode(response["raw_text"], 2, True)
            else:
                decoded = decode(
                    json.dumps(
                        {"hypothesis": "CPU proposal", "candidates": candidates}
                    ),
                    2,
                )
            if value(root, f"{batch}/decoded.json") != decoded:
                raise ValueError("response parsing differs")
            trials = value(root, f"{batch}/trials.json")
            if len(trials) != 2:
                raise ValueError("wrong proposal count")
            for j, (trial, proposal) in enumerate(
                zip(trials, decoded["slots"], strict=True)
            ):
                if (
                    trial["slot"] != offset + j + 1
                    or trial["program"] != proposal["submitted"]
                    or trial["prediction"] != proposal["prediction"]
                ):
                    raise ValueError("submitted proposal differs")
                check_trial(root, trial, manifest)
                if (trial["stage"] == "API") != bool(
                    model_batch and response.get("api_error")
                ):
                    raise ValueError("API failure classification differs")
                note_error = proposal["prediction_error"]
                if proposal["prediction"] and proposal["prediction"][
                    "reference_slot"
                ] not in {t["slot"] for t in history if t["valid"]}:
                    note_error = "reference was not visible as valid before this batch"
                if trial["prediction_error"] != note_error:
                    raise ValueError("prediction visibility differs")
                if trial["valid"] and not math.isclose(
                    trial["loss"],
                    error(
                        trial["rates"],
                        manifest["targets"][target]["rates"],
                        manifest["scale"],
                    ),
                    abs_tol=1e-12,
                ):
                    raise ValueError("target error differs")
                if (
                    assess(trial, history, manifest["scale"])
                    != trial["prediction_assessment"]
                ):
                    raise ValueError("prediction outcome differs")
            for trial in trials:
                archive.observe(trial)
            history.extend(trials)
        for budget in manifest["prefixes"]:
            if value(root, f"{directory}/prefix-{budget}.json") != {
                "cell": cell,
                **summarize(history, budget, manifest["tolerance"]),
            }:
                raise ValueError("prefix arithmetic differs")
        histories[target, seed, arm] = history
    return describe(manifest, histories, responses)


def verify(root):
    index = read(root / "sha256.json")
    paths = {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.name != "sha256.json"
    }
    if set(index) != paths:
        raise ValueError("archive file set differs")
    for name, digest in index.items():
        path = root / name
        if (
            not path.resolve().is_relative_to(root.resolve())
            or file_sha256(path) != digest
        ):
            raise ValueError(f"unsafe or changed archive file: {name}")
    manifest = read(root / "manifest.json")
    for name, digest in manifest["sources"].items():
        if file_sha256(root / "sources" / name) != digest:
            raise ValueError("frozen source copy differs")
    if audit(root) != read(root / "aggregate.json"):
        raise ValueError("aggregate differs")
    return {
        "cells": len(manifest["cells"]),
        "slots": len(manifest["cells"]) * max(manifest["prefixes"]),
        "files": len(index),
        "scope": "compact evidence, not independent waveform replay",
    }


def archive(source, destination):
    manifest = read(destination / "manifest.json")
    maximum = max(manifest["prefixes"])
    if not (source / f"prefix-{maximum}-complete.json").exists():
        raise ValueError("panel incomplete; do not publish a complete aggregate")
    identifiers = set()
    timings = []

    def copy(path, relative):
        target = destination / (str(relative) + ".gz")
        target.parent.mkdir(parents=True, exist_ok=True)
        data = gzip.compress(path.read_bytes(), mtime=0)
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"immutable archive evidence differs: {target}")
        target.write_bytes(data)

    for path in sorted((source / "panel").rglob("*.json")):
        copy(path, path.relative_to(source))
        if path.name == "trials.json":
            identifiers.update(t["cache_id"] for t in read(path) if t["cache_id"])
    for identifier in sorted(identifiers):
        for name in (
            "result.json",
            "program.json",
            "driver.log",
            "run/program.S",
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
    for budget in manifest["prefixes"]:
        shutil.copyfile(
            source / f"prefix-{budget}-complete.json",
            destination / f"prefix-{budget}-complete.json",
        )
    for cell in manifest["cells"]:
        directory = source / "panel" / cell["target"] / str(cell["seed"]) / cell["arm"]
        start = (directory / "identity.json").stat().st_mtime
        timings.append(
            {
                "cell": cell,
                "identity_mtime_unix": start,
                "prefix_summary_mtime_unix": {
                    str(n): (directory / f"prefix-{n}.json").stat().st_mtime
                    for n in manifest["prefixes"]
                },
                "scope": "Observed checkpoint timestamps; elapsed spans include worker/stage waits, not exclusive compute time.",
            }
        )
    (destination / "execution_timings.json").write_text(
        json.dumps(timings, indent=2) + "\n"
    )
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
