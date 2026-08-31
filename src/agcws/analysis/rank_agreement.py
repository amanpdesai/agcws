"""Dependency-free rank agreement for cross-library power results."""
from __future__ import annotations

import hashlib
import json
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
