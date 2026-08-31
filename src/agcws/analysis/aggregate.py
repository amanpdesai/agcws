"""Aggregate proposal-counted run summaries without external statistics packages."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
import random


def aggregate_summaries(records: Iterable[dict]) -> list[dict]:
    """Aggregate run summaries by policy and design.

    Every input record is retained in the denominator, including right-censored
    unsolved runs. Records may include ``policy`` and ``design`` metadata; an
    absent design is grouped as ``unknown``.
    """
    groups: defaultdict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for record in records:
        groups[(str(record.get("policy", "unknown")),
                str(record.get("design", "unknown")),
                str(record.get("target", "unknown")))].append(record)
    output = []
    for (policy, design, target), values in sorted(groups.items()):
        count = len(values)
        failure_stages = {stage: sum(
            int(value.get("validity_failures", {}).get(stage, 0)) for value in values
        ) for stage in ("SCHEMA", "PROTOCOL", "FUNCTIONAL", "USEFUL_WORK")}
        auc_ci = bootstrap_mean_ci(
            [value["auc_best_so_far"] for value in values], seed=0
        )
        eval_ci = bootstrap_mean_ci(
            [value["evaluations_to_target"] for value in values], seed=1
        )
        output.append({
            "policy": policy,
            "design": design,
            "target": target,
            "runs": count,
            "solve_rate": sum(bool(value.get("solved", False)) for value in values) / count,
            "mean_auc_best_so_far": sum(float(value["auc_best_so_far"])
                                         for value in values) / count,
            "mean_evaluations_to_target": sum(float(value["evaluations_to_target"])
                                               for value in values) / count,
            "auc_best_so_far_ci95": auc_ci,
            "evaluations_to_target_ci95": eval_ci,
            "valid_trials": sum(int(value.get("valid_trials", 0)) for value in values),
            "simulations": sum(int(value.get("simulations", 0)) for value in values),
            "tokens_in": sum(int(value.get("tokens_in", 0)) for value in values),
            "tokens_out": sum(int(value.get("tokens_out", 0)) for value in values),
            "validity_failures": failure_stages,
        })
    return output


def bootstrap_mean_ci(values: Iterable[float], *, samples: int = 2000,
                      seed: int = 0, confidence: float = 0.95) -> dict[str, float]:
    """Return a deterministic percentile bootstrap CI for a sample mean."""
    data = [float(value) for value in values]
    if not data or samples <= 0 or not 0.0 < confidence < 1.0:
        raise ValueError("values, samples, and confidence must be valid")
    rng = random.Random(seed)
    means = [sum(rng.choice(data) for _ in data) / len(data) for _ in range(samples)]
    means.sort()
    alpha = (1.0 - confidence) / 2.0

    def percentile(q: float) -> float:
        position = q * (len(means) - 1)
        lower = int(position)
        upper = min(lower + 1, len(means) - 1)
        fraction = position - lower
        return means[lower] + fraction * (means[upper] - means[lower])

    return {"mean": sum(data) / len(data), "lower": percentile(alpha),
            "upper": percentile(1.0 - alpha)}
