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
from agcws.policies.vertex import VertexAgent
from agcws.provenance import file_sha256
from experiments.ibex_temporal_v1.program import (
    SCHEMA,
    mutate,
    random_program,
    validate,
)

PROMPT = """Construct bounded CPU programs to match the requested eight-bin activity profile.
Return strict JSON {"hypothesis": "short testable prediction", "candidates": [programs]}.
Use the complete schema. Return the requested number of candidates. Use feedback to
change complete programs, including operands, instruction mix, segment placement and
dependencies. Do not merely change a few scalar fields. Do not modify hardware or tools.
Exactly 4096 semantic body operations must finish inside the 200000-cycle window.
Missing and invalid candidates consume budget. Do not repeat failed strategies.
"""

SEMANTICS = """Ibex is an in-order RV32IM CPU, fast multiplier, instruction cache off.
registers initializes eight mutable 32-bit registers, addressed by indices 0..7.
add/mul wrap modulo 2^32; shifts mask the amount to five bits; divu is unsigned
and returns 0xffffffff for divisor zero. Division with nonzero divisor stalls
the pipeline substantially longer than zero division or ordinary ALU operations.
cmovz copies register b to dst only if register a is zero; it lowers to a real
conditional branch. Memory holds 64 words initialized by (memory_seed+i*0x9e3779b9)
modulo 2^32. load/store index memory by the low six bits of register a; stores
write register b. Registers and memory persist across iterations and segments.
Each segment waits until release cycles after measurement start, then executes
its body iterations times using a real loop. Releases already passed do not
rewind time. Waiting is an active CSR/branch loop, NOT sleep or zero activity.
The controller measures core-net bit changes, excluding clocks and CSR counters;
lower instruction retirement rate need not imply higher or lower switching.
All register and memory results are independently reference-checked.
"""


class ProgramAgent(VertexAgent):
    max_output_tokens = 8192
    thinking_budget = 512
    proposal_attempts = 1

    @staticmethod
    def build_payload(adapter, goal, history, n, system_prompt):
        valid = sorted((t for t in history if t["valid"]), key=lambda t: t["loss"])[:4]
        selected = {t["slot"]: t for t in [*valid, *history[-4:]]}
        compact = [
            {
                k: t[k]
                for k in (
                    "slot",
                    "program",
                    "valid",
                    "reason",
                    "loss",
                    "rates",
                    "residual",
                )
            }
            for t in selected.values()
        ]
        return json.dumps(
            {
                "system_prompt": system_prompt,
                "semantics": SEMANTICS,
                "schema": SCHEMA,
                "goal": goal,
                "history": compact,
                "batch_size": n,
            },
            sort_keys=True,
        )


def key(program):
    return hashlib.sha256(json.dumps(program, sort_keys=True).encode()).hexdigest()


def error(rates, target, scale):
    if len(rates) != 8 or len(target) != 8 or scale <= 0:
        raise ValueError("eight bins and a positive frozen scale required")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rates, target)) / 8) / scale


def measured(program, root, fingerprint):
    try:
        validate(program)
    except jsonschema.ValidationError as exc:
        return {"valid": False, "stage": "SCHEMA", "reason": exc.message}, False
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
                    "experiments.ibex_temporal_v1.evaluate",
                    "--program",
                    f"out/cache/{identifier}/program.json",
                    "--out",
                    f"out/cache/{identifier}/run",
                    "--activity",
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
        record.update(cache_id=identifier, evaluation_s=time.monotonic() - started)
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        return record, False


def search(manifest_path, root, target_name, policy, seed):
    manifest = json.loads(manifest_path.read_text())
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"changed frozen development source: {name}")
    if (
        target_name not in manifest["targets"]
        or seed not in manifest["seeds"]
        or policy not in manifest["policies"]
    ):
        raise ValueError("run outside declared development panel")
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
    if policy == "agent":
        config._load_dotenv()
        os.environ["AGCWS_VERTEX_TIMEOUT_S"] = "0"
        os.environ["AGCWS_VERTEX_TIMEOUT_MS"] = "120000"
        os.environ["AGCWS_VERTEX_RETRY_ATTEMPTS"] = "1"
        agent = ProgramAgent.from_vertex(
            PROMPT, model=manifest["model"], project=os.environ["AGCWS_GCP_PROJECT"]
        )
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
            if offset == 0:
                candidates = initial
            elif policy == "agent":
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
                parents = sorted(
                    (t for t in history if t["valid"]), key=lambda t: t["loss"]
                )[:4]
                candidates = [
                    mutate(rng.choice(parents)["program"], rng)
                    if parents
                    else random_program(rng)
                    for _ in range(n)
                ]
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
                    "valid": result["valid"],
                    "stage": result["stage"],
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
                    "model": manifest["model"] if policy == "agent" else None,
                    "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
                }
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
    parser.add_argument(
        "--policy", choices=["random", "mutation", "agent"], required=True
    )
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    search(args.manifest, args.root, args.target, args.policy, args.seed)
