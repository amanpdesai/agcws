"""Budget-fair search runner independent of any particular evaluator backend."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Callable

from agcws.adapters.base import DesignAdapter, SimResult
from agcws.goals.loss import loss
from agcws.nodes.power import PowerProfile
from agcws.nodes.validation import validate_static
from agcws.policies.base import SearchPolicy
from agcws.telemetry.ledger import Trial


def _jsonable(value):
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "value"):
        return value.value
    return value


def run_search(
    adapter: DesignAdapter,
    policy: SearchPolicy,
    goal,
    evaluate: Callable[[dict], PowerProfile],
    *,
    budget: int = 200,
    batch_size: int = 8,
    seed: int = 0,
    design: str | None = None,
    p_min: float | None = None,
    p_max: float | None = None,
    output_dir: Path | None = None,
) -> list[Trial]:
    """Run exactly ``budget`` proposal slots, including invalid candidates."""
    if budget <= 0 or batch_size <= 0:
        raise ValueError("budget and batch_size must be positive")
    trials: list[Trial] = []
    best = float("inf")
    curve: list[float] = []
    proposal_index = 0
    while proposal_index < budget:
        requested = min(batch_size, budget - proposal_index)
        candidates = policy.propose(adapter, goal, trials, requested)
        # Missing candidates consume their requested slots just like malformed
        # LLM output; this is the primary fairness unit.
        for slot in range(requested):
            workload = candidates[slot] if slot < len(candidates) else {}
            started = time.monotonic()
            validity = validate_static(adapter, workload)
            profile = None
            if validity.valid:
                profile = evaluate(workload)
                if not profile.valid:
                    validity = adapter.validate_result(SimResult(False, True, False, profile.useful_work))
            if validity.valid and profile is not None:
                current = loss(profile, goal, p_min=p_min, p_max=p_max)
                best = min(best, current)
                sim_count = 1
            else:
                current = float("inf")
                sim_count = 0
            curve.append(best)
            trials.append(Trial(
                trial_id=f"{policy.name}-{proposal_index + slot:05d}",
                design=design or adapter.name,
                goal=goal,
                policy=policy.name,
                seed=seed,
                workload=workload,
                validity=validity,
                profile=profile,
                loss=None if not validity.valid else current,
                wall_clock_s=time.monotonic() - started,
                sim_count=sim_count,
                model=getattr(policy, "model", ""),
                prompt_hash=getattr(policy, "prompt_hash", ""),
            ))
        proposal_index += requested
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "trials.jsonl").write_text("\n".join(
            json.dumps({k: _jsonable(v) for k, v in asdict(trial).items()}, sort_keys=True)
            for trial in trials
        ) + "\n")
        (output_dir / "best_so_far.json").write_text(json.dumps({"error": curve}) + "\n")
    return trials
