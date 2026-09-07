"""Proposal-counted temporal comparison with predictions recorded before execution."""

import argparse
import hashlib
import json
import os
import random
import subprocess
import time
from itertools import pairwise
from pathlib import Path

from agcws import config
from agcws.provenance import file_sha256
from experiments.ibex_temporal_v3.coverage import BehaviorArchive
from experiments.ibex_temporal_v3.program import canonical, random_program
from experiments.ibex_temporal_v3.search import error, verify_runtime
from experiments.ibex_temporal_v4.cache import measured
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.evaluate import write
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.native_schema import serving_schema
from experiments.ibex_temporal_v4.notebook import assess
from experiments.ibex_temporal_v4.transport import client, request

POLICIES = ("random", "coverage", "agent-base", "agent-grounded")


def search(manifest_path, root, target_name, policy, seed):
    manifest = json.loads(manifest_path.read_text())
    verify_runtime(manifest, root)
    committed = subprocess.check_output(["git", "show", f"HEAD:{manifest_path}"])
    if hashlib.sha256(committed).hexdigest() != file_sha256(manifest_path):
        raise ValueError("manifest must be committed before running")
    if (
        policy not in manifest["policies"]
        or seed not in manifest["seeds"]
        or target_name not in manifest["targets"]
    ):
        raise ValueError("cell outside frozen panel")
    output = root / "panel" / target_name / f"seed-{seed}" / policy
    output.mkdir(parents=True, exist_ok=False)
    write(
        output / "manifest.json",
        {
            "study_sha256": file_sha256(manifest_path),
            "target": target_name,
            "policy": policy,
            "seed": seed,
        },
    )
    agent = policy.startswith("agent-")
    api = None
    if agent:
        config._load_dotenv()
        api = client(os.environ["AGCWS_GCP_PROJECT"])
    rng = random.Random(seed)
    initial = [random_program(rng) for _ in range(2)]
    archive = BehaviorArchive()
    target = manifest["targets"][target_name]["rates"]
    scale, tolerance, budget = (
        manifest["scale"],
        manifest["tolerance"],
        manifest["budget"],
    )
    history, batches, curve, spend, best = [], [], [], 0.0, 1.0
    started = time.monotonic()
    with (output / "trials.jsonl").open("w") as ledger:
        for offset in range(0, budget, 2):
            n = min(2, budget - offset)
            info = {
                "tokens_in": 0,
                "tokens_out": 0,
                "est_cost_usd": 0.0,
                "usage_unknown": False,
            }
            modes, references = ["initial" if offset == 0 else policy] * n, [None] * n
            items = None
            if offset == 0:
                candidates = initial[:n]
            elif agent:
                if spend >= 1.0:
                    raise RuntimeError("development per-run $1 cap reached")
                contents = payload(
                    history,
                    {"profile": target, "scale": scale, "tolerance": tolerance},
                    n,
                    grounded=policy == "agent-grounded",
                )
                (output / f"payload-{offset + 1}.json").write_text(contents + "\n")
                try:
                    info = request(
                        api,
                        manifest["model"],
                        contents,
                        manifest,
                        serving_schema(n, True),
                    )
                except Exception as exc:
                    info.update(
                        exception=type(exc).__name__,
                        message=str(exc),
                        raw_text="",
                        usage_unknown=True,
                    )
                decoded = decode(info["raw_text"], n, predictions=True)
                info["decoded"] = decoded
                info["payload_sha256"] = file_sha256(
                    output / f"payload-{offset + 1}.json"
                )
                items = decoded["slots"]
                candidates = [s["submitted"] for s in items]
                spend += info["est_cost_usd"]
            elif policy == "random":
                candidates = [random_program(rng) for _ in range(n)]
            else:
                proposals = [archive.propose(rng) for _ in range(n)]
                candidates = [p for p, _ in proposals]
                references = [m.get("parent_slot") for _, m in proposals]
                modes = [m["mode"] for _, m in proposals]
            # This record exists before either candidate's simulator is invoked.
            batches.append({"first_slot": offset + 1, "requested_slots": n, **info})
            write(output / "batches.json", batches)
            visible_references = {t["slot"] for t in history if t["valid"]}
            for j in range(n):
                program = candidates[j]
                result, hit = measured(
                    program, root, manifest["measurement_fingerprint"]
                )
                rates = result["profile"]["window_rates"] if result["valid"] else None
                loss = error(rates, target, scale) if rates is not None else None
                if loss is not None:
                    best = min(best, loss)
                curve.append(best)
                note = items[j]["prediction"] if items else None
                note_error = items[j]["prediction_error"] if items else None
                if note is not None:
                    references[j] = note["reference_slot"]
                    if note["reference_slot"] not in visible_references:
                        note_error = (
                            "reference was not visible as valid before this batch"
                        )
                trial = {
                    "slot": offset + j + 1,
                    "program": program,
                    "canonical_program": canonical(program)
                    if result.get("cache_id")
                    else None,
                    "valid": result["valid"],
                    "stage": result["stage"],
                    "reason": result["reason"],
                    "schema_path": result.get("schema_path"),
                    "allocation": result.get("allocation"),
                    "feedback": result.get("feedback"),
                    "execution": result.get("execution"),
                    "rates": rates,
                    "loss": loss,
                    "best_loss": best,
                    "residual": [(a - b) / scale for a, b in zip(rates, target)]
                    if rates
                    else None,
                    "prediction": note,
                    "prediction_error": note_error,
                    "reference_slot": references[j],
                    "proposal_mode": modes[j],
                    "cache_id": result.get("cache_id"),
                    "cache_hit": hit,
                    "simulations_executed": int(
                        not hit and bool(result.get("cache_id"))
                    ),
                    "tokens_in": info["tokens_in"] // n
                    + int(j < info["tokens_in"] % n),
                    "tokens_out": info["tokens_out"] // n
                    + int(j < info["tokens_out"] % n),
                    "est_cost_usd": info["est_cost_usd"] / n,
                    "model": manifest["model"] if agent else None,
                }
                trial["prediction_assessment"] = assess(trial, history, scale)
                archive.observe(trial)
                history.append(trial)
                ledger.write(json.dumps(trial) + "\n")
                ledger.flush()
            print(target_name, policy, seed, offset + n, best, flush=True)
    solved = next(
        (
            t["slot"]
            for t in history
            if t["loss"] is not None and t["loss"] <= tolerance
        ),
        None,
    )
    write(
        output / "summary.json",
        {
            "target": target_name,
            "policy": policy,
            "seed": seed,
            "budget": budget,
            "auc": sum((a + b) / 2 for a, b in pairwise(curve)),
            "final_loss": best,
            "solved": solved is not None,
            "evaluations_to_target": solved or budget,
            "right_censored": solved is None,
            "valid_slots": sum(t["valid"] for t in history),
            "behavior_cells": len(archive.elites),
            "est_cost_usd": spend,
            "unknown_usage_batches": sum(b["usage_unknown"] for b in batches),
            "wall_clock_s": time.monotonic() - started,
            "phase": "development-only",
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("manifest", "root"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--policy", choices=POLICIES, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    search(args.manifest, args.root, args.target, args.policy, args.seed)
