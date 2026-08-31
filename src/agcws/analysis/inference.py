"""Deterministic, dependency-free paired inference for experiment summaries."""
from __future__ import annotations

from collections.abc import Iterable
import math


def paired_permutation_pvalue(left: Iterable[float], right: Iterable[float]) -> float:
    """Return an exact two-sided sign-flip p-value for paired observations.

    This tests the mean paired difference and is intentionally exact for the
    small target/design panels used by the study. Ties contribute zero and are
    not included in the sign-flip denominator.
    """
    left_values, right_values = list(left), list(right)
    if len(left_values) != len(right_values):
        raise ValueError("paired samples must have equal length")
    differences = [float(a) - float(b) for a, b in zip(left_values, right_values)]
    if not differences or any(not math.isfinite(value) for value in differences):
        raise ValueError("paired samples must be non-empty and finite")
    differences = [value for value in differences if value != 0.0]
    if not differences:
        return 1.0
    observed = abs(sum(differences))
    extreme = 0
    total = 1 << len(differences)
    for mask in range(total):
        signed = sum(value if mask & (1 << index) else -value
                     for index, value in enumerate(differences))
        if abs(signed) >= observed - 1e-15:
            extreme += 1
    return extreme / total


def holm_bonferroni(pvalues: Iterable[float]) -> list[float]:
    """Return Holm-adjusted p-values in the original input order."""
    values = [float(value) for value in pvalues]
    if any(not 0.0 <= value <= 1.0 for value in values):
        raise ValueError("p-values must lie in [0, 1]")
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [0.0] * len(values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(values) - rank) * values[index]))
        adjusted[index] = running
    return adjusted


def rank_biserial_effect(left: Iterable[float], right: Iterable[float]) -> float:
    """Return matched-pairs rank-biserial effect in [-1, 1]."""
    differences = [float(a) - float(b) for a, b in zip(left, right)]
    differences = [value for value in differences if value != 0.0]
    if not differences or any(not math.isfinite(value) for value in differences):
        raise ValueError("paired samples must contain finite nonzero differences")
    ranked = sorted((abs(value), value > 0.0) for value in differences)
    positive = sum(rank + 1 for rank, (_, is_positive) in enumerate(ranked) if is_positive)
    negative = sum(rank + 1 for rank, (_, is_positive) in enumerate(ranked) if not is_positive)
    return (positive - negative) / (positive + negative)
