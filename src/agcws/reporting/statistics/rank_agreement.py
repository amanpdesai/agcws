"""Dependency-free rank agreement for cross-library power results."""
from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Iterable


def workload_id(workload: dict) -> str:
    encoded = json.dumps(workload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and values[order[end]] == values[order[index]]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for position in order[index:end]:
            ranks[position] = rank
        index = end
    return ranks


def rank_agreement(left: Iterable[tuple[str, float]], right: Iterable[tuple[str, float]]) -> dict:
    """Return Spearman rho and shared workload count for two result sets."""
    lhs, rhs = dict(left), dict(right)
    keys = sorted(lhs.keys() & rhs.keys())
    if len(keys) < 2:
        raise ValueError("at least two shared workloads are required")
    x, y = _ranks([lhs[key] for key in keys]), _ranks([rhs[key] for key in keys])
    mean_x, mean_y = sum(x) / len(x), sum(y) / len(y)
    numerator = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    denom_x = sum((a - mean_x) ** 2 for a in x) ** 0.5
    denom_y = sum((b - mean_y) ** 2 for b in y) ** 0.5
    rho = numerator / (denom_x * denom_y) if denom_x and denom_y else 1.0
    return {"shared_workloads": len(keys), "spearman_rho": rho}


def bootstrap_rank_ci(left: Iterable[tuple[str, float]],
                      right: Iterable[tuple[str, float]], *,
                      samples: int = 2000, seed: int = 0,
                      confidence: float = 0.95) -> dict[str, float]:
    """Return a deterministic percentile bootstrap CI for Spearman rho."""
    lhs, rhs = dict(left), dict(right)
    keys = sorted(lhs.keys() & rhs.keys())
    if len(keys) < 2 or samples <= 0 or not 0.0 < confidence < 1.0:
        raise ValueError("shared data, samples, and confidence must be valid")
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        selected = [keys[rng.randrange(len(keys))] for _ in keys]
        estimates.append(rank_agreement(
            [(str(i), lhs[key]) for i, key in enumerate(selected)],
            [(str(i), rhs[key]) for i, key in enumerate(selected)],
        )["spearman_rho"])
    estimates.sort()
    alpha = (1.0 - confidence) / 2.0

    def percentile(q: float) -> float:
        position = q * (len(estimates) - 1)
        lower = int(position)
        upper = min(lower + 1, len(estimates) - 1)
        return estimates[lower] + (position - lower) * (estimates[upper] - estimates[lower])

    return {"mean": rank_agreement([(k, lhs[k]) for k in keys],
                                    [(k, rhs[k]) for k in keys])["spearman_rho"],
            "lower": percentile(alpha), "upper": percentile(1.0 - alpha)}
