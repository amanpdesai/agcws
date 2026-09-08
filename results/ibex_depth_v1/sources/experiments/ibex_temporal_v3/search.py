"""Proposal-counted development search; all simulation passes a shared cache."""

import argparse
import fcntl
import hashlib
import json
import math
import os
import random
import subprocess
import time
from itertools import pairwise
from pathlib import Path

import jsonschema

from agcws import config
from agcws.provenance import file_sha256
from experiments.ibex_temporal_v3.program import (
    canonical,
    allocation,
    random_program,
)

from experiments.ibex_temporal_v3.agent import TemporalAgent, prompt
from experiments.ibex_temporal_v3.context import load_context
from experiments.ibex_temporal_v3.coverage import BehaviorArchive

POLICIES = (
    "random",
    "coverage",
    "agent-base",
    "agent-context",
    "agent-correction",
    "agent-combined",
)


def key(program):
    return hashlib.sha256(json.dumps(program, sort_keys=True).encode()).hexdigest()


def error(rates, target, scale):
    if len(rates) != 8 or len(target) != 8 or scale <= 0:
        raise ValueError("eight bins and a positive frozen scale required")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rates, target)) / 8) / scale


def measured(program, root, fingerprint):
    try:
        program = canonical(program)
    except jsonschema.ValidationError as exc:
        return {
            "valid": False,
            "stage": "SCHEMA",
            "reason": exc.message,
            "schema_path": list(exc.absolute_path),
        }, False
    except ValueError as exc:
        return {"valid": False, "stage": "PROTOCOL", "reason": str(exc)}, False
    identifier = key({"program": program, "measurement": fingerprint})
    locks = root / "locks"
    locks.mkdir(exist_ok=True)
    with (locks / f"{identifier}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        directory = root / "cache" / identifier
        record_path = directory / "result.json"
        if record_path.exists():
            return json.loads(record_path.read_text()), True
        directory.mkdir(parents=True, exist_ok=False)
        source = directory / "program.json"
        source.write_text(json.dumps(program, indent=2) + "\n")
        environment = {
            **os.environ,
            "AGCWS_CONTAINER_IMAGE": "agcws:window-validation-v1",
            "AGCWS_CONTAINER_OUTPUT": str(root.resolve()),
        }
        started = time.monotonic()
        with (directory / "driver.log").open("w") as log:
            result = subprocess.run(
                [
                    "bash",
                    "docker/run.sh",
                    "python3",
                    "-m",
                    "experiments.ibex_temporal_v3.evaluate",
                    "--program",
                    f"out/cache/{identifier}/program.json",
                    "--out",
                    f"out/cache/{identifier}/run",
                ],
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        output = directory / "run"
        if result.returncode:
            diagnostic = (directory / "driver.log").read_text()
            if (
                "useful work or observation window did not complete in time"
                in diagnostic
            ):
                record = {
                    "valid": False,
                    "stage": "USEFUL_WORK",
                    "reason": "body or fixed observation did not complete in the declared window",
                }
            elif "architectural reference mismatch" in diagnostic:
                record = {
                    "valid": False,
                    "stage": "FUNCTIONAL",
                    "reason": "architectural state mismatch",
                }
            else:
                raise RuntimeError(
                    f"evaluator infrastructure failed; inspect {directory}/driver.log"
                )
        else:
            profile = json.loads((output / "profile.json").read_text())
            record = {"valid": True, "stage": None, "reason": "", "profile": profile}
        feedback_path = output / "feedback.json"
        record["feedback"] = (
            json.loads(feedback_path.read_text()) if feedback_path.exists() else None
        )
        if record["valid"] and (
            record["feedback"] is None
            or any(
                record["feedback"][k] != record["profile"][k]
                for k in ("begin_tick", "end_tick")
            )
        ):
            raise RuntimeError("feedback is absent or differs from the activity window")
        record.update(
            cache_id=identifier,
            allocation=allocation(program),
            evaluation_s=time.monotonic() - started,
        )
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        return record, False


def verify_runtime(manifest, root):
    from importlib.metadata import version

    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"changed frozen development source: {name}")
    binary = (
        root
        / "toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system"
    )
    if file_sha256(binary) != manifest["measurement"]["binary_sha256"]:
        raise ValueError("changed simulator binary")
    image = subprocess.check_output(
        [
            "docker",
            "image",
            "inspect",
            "agcws:window-validation-v1",
            "--format",
            "{{.Id}}",
        ],
        text=True,
    ).strip()
    if image != manifest["measurement"]["image_id"]:
        raise ValueError("changed container image")
    for name, expected in manifest["packages"].items():
        if version(name) != expected:
            raise ValueError(f"changed package: {name}")
    for name in ("temperature", "top_p", "thinking_budget", "max_output_tokens"):
        if getattr(TemporalAgent, name) != manifest[name]:
            raise ValueError(f"changed model sampling configuration: {name}")


def search(manifest_path, root, target_name, policy, seed):
    manifest = json.loads(manifest_path.read_text())
    verify_runtime(manifest, root)
    if (
        target_name not in manifest["targets"]
        or seed not in manifest["seeds"]
        or policy not in manifest["policies"]
    ):
        raise ValueError("run outside declared development panel")
    source_arm = policy in ("agent-context", "agent-combined")
    correction_arm = policy in ("agent-correction", "agent-combined")
    system_prompt = prompt(source_arm, correction_arm)
    if (
        hashlib.sha256(system_prompt.encode()).hexdigest()
        != manifest["prompts"][policy]
    ):
        raise ValueError("changed frozen prompt")
    output = root / "panel" / target_name / f"seed-{seed}" / policy
    output.mkdir(parents=True, exist_ok=False)
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "study_sha256": file_sha256(manifest_path),
                "target": target_name,
                "policy": policy,
                "seed": seed,
            },
            indent=2,
        )
        + "\n"
    )
    rng = random.Random(seed)
    initial = [random_program(rng) for _ in range(2)]
    target = manifest["targets"][target_name]["rates"]
    scale, tolerance, budget = (
        manifest["scale"],
        manifest["tolerance"],
        manifest["budget"],
    )
    agent = None
    if policy.startswith("agent-"):
        config._load_dotenv()
        os.environ["AGCWS_VERTEX_TIMEOUT_S"] = "0"
        os.environ["AGCWS_VERTEX_TIMEOUT_MS"] = "120000"
        os.environ["AGCWS_VERTEX_RETRY_ATTEMPTS"] = "1"
        agent = TemporalAgent.from_vertex(
            system_prompt,
            model=manifest["model"],
            project=os.environ["AGCWS_GCP_PROJECT"],
        )
        agent.correction = correction_arm
        if source_arm:
            agent.source_context = load_context(
                Path(manifest["context_root"]), manifest["context_sha256"]
            )
            if key(agent.source_context) != manifest["context_payload_sha256"]:
                raise ValueError("changed source-context payload")
            (output / "source_context.json").write_text(
                json.dumps(agent.source_context, indent=2) + "\n"
            )
    archive = BehaviorArchive()
    history, batches, best, curve, spend = [], [], 1.0, [], 0.0
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
            references = [None] * n
            reference = min(
                (t for t in history if t["valid"]),
                key=lambda t: t["loss"],
                default=None,
            )
            if correction_arm and reference is not None:
                references = [reference["slot"]] * n
            proposal_modes = ["initial" if offset == 0 else policy] * n
            if offset == 0:
                candidates = initial
            elif policy.startswith("agent-"):
                if spend >= 1.0:
                    raise RuntimeError("development per-run $1 model cap reached")
                try:
                    candidates = agent.propose(
                        None,
                        {"profile": target, "scale": scale, "tolerance": tolerance},
                        history,
                        n,
                    )
                except ValueError as exc:
                    candidates = []
                    info["parse_error"] = str(exc)
                info.update(agent.last_usage)
                info["diagnostics"] = agent.last_diagnostics
                info["usage_unknown"] = bool(
                    agent.last_diagnostics.get("usage_unknown", False)
                )
                info["est_cost_usd"] = (
                    info["tokens_in"] * manifest["input_rate"]
                    + info["tokens_out"] * manifest["output_rate"]
                ) / 1e6
                spend += info["est_cost_usd"]
            elif policy == "random":
                candidates = [random_program(rng) for _ in range(n)]
            else:
                proposals = [archive.propose(rng) for _ in range(n)]
                candidates = [p for p, _ in proposals]
                references = [meta.get("parent_slot") for _, meta in proposals]
                proposal_modes = [meta["mode"] for _, meta in proposals]
            batches.append({"first_slot": offset + 1, "requested_slots": n, **info})
            (output / "batches.json").write_text(json.dumps(batches, indent=2) + "\n")
            for j in range(n):
                program = candidates[j] if j < len(candidates) else {}
                result, hit = measured(
                    program, root, manifest["measurement_fingerprint"]
                )
                rates = result["profile"]["window_rates"] if result["valid"] else None
                loss = error(rates, target, scale) if rates is not None else None
                if loss is not None:
                    best = min(best, loss)
                curve.append(best)
                trial = {
                    "slot": offset + j + 1,
                    "program": program,
                    "canonical_program": canonical(program)
                    if result.get("cache_id")
                    else None,
                    "feedback": result.get("feedback"),
                    "schema_path": result.get("schema_path"),
                    "reference_slot": references[j],
                    "proposal_mode": proposal_modes[j],
                    "valid": result["valid"],
                    "stage": result["stage"],
                    "allocation": result.get("allocation"),
                    "reason": result["reason"],
                    "rates": rates,
                    "loss": loss,
                    "best_loss": best,
                    "residual": [(a - b) / scale for a, b in zip(rates, target)]
                    if rates
                    else None,
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
                    "model": manifest["model"] if policy.startswith("agent-") else None,
                    "prompt_sha256": hashlib.sha256(system_prompt.encode()).hexdigest(),
                }
                parent = next((t for t in history if t["slot"] == references[j]), None)
                trial["rate_delta_from_reference"] = (
                    [x - y for x, y in zip(rates, parent["rates"])]
                    if rates is not None and parent is not None
                    else None
                )
                archive.observe(trial)
                history.append(trial)
                ledger.write(json.dumps(trial) + "\n")
                ledger.flush()
            print(target_name, policy, seed, offset + n, best, flush=True)
    solved_at = next(
        (
            t["slot"]
            for t in history
            if t["loss"] is not None and t["loss"] <= tolerance
        ),
        None,
    )
    summary = {
        "target": target_name,
        "policy": policy,
        "seed": seed,
        "budget": budget,
        "auc": sum((a + b) / 2 for a, b in pairwise(curve)),
        "final_loss": best,
        "solved": solved_at is not None,
        "evaluations_to_target": solved_at or budget,
        "right_censored": solved_at is None,
        "valid_slots": sum(t["valid"] for t in history),
        "behavior_cells": len(archive.elites),
        "est_cost_usd": spend,
        "unknown_usage_batches": sum(b["usage_unknown"] for b in batches),
        "wall_clock_s": time.monotonic() - started,
        "phase": "development-only",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("manifest", "root"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--policy", choices=POLICIES, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    search(args.manifest, args.root, args.target, args.policy, args.seed)
