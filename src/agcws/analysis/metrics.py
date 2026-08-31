"""Deterministic metrics for proposal-counted search runs."""
from __future__ import annotations

import math
from collections.abc import Iterable


def best_so_far_auc(errors: Iterable[float], *, budget: int | None = None) -> float:
    """Return trapezoidal area of a best-so-far error curve.

    The x-axis is the proposal index, starting at one. Infinite values from
    runs with no valid candidate are treated as one (the normalized worst
    error); this keeps an invalid prefix from producing an infinite summary.
    ``budget`` optionally pads a short curve with its final value.
    """
    values = [float(value) for value in errors]
    if budget is not None:
        if budget <= 0:
            raise ValueError("budget must be positive")
        if not values:
            values = [1.0] * budget
        elif len(values) < budget:
            values.extend([values[-1]] * (budget - len(values)))
        else:
            values = values[:budget]
    if len(values) < 2:
        return 0.0
    finite = [1.0 if not math.isfinite(value) else max(0.0, value) for value in values]
    return sum((left + right) / 2.0 for left, right in zip(finite, finite[1:]))


def evaluations_to_target(errors: Iterable[float], epsilon: float) -> int | None:
    """Return the first proposal index within tolerance, or ``None``."""
    if epsilon < 0:
        raise ValueError("epsilon must be non-negative")
    for index, value in enumerate(errors, start=1):
        if math.isfinite(float(value)) and float(value) <= epsilon:
            return index
    return None


def summarize_run(errors: Iterable[float], epsilon: float, *, budget: int | None = None) -> dict:
    """Summarize one run without dropping unsolved, right-censored trials."""
    values = list(errors)
    target = evaluations_to_target(values, epsilon)
    effective_budget = budget if budget is not None else len(values)
    if effective_budget <= 0:
        raise ValueError("run budget must be positive")
    return {
        "budget": effective_budget,
        "auc_best_so_far": best_so_far_auc(values, budget=effective_budget),
        "solved": target is not None,
        "evaluations_to_target": target if target is not None else effective_budget,
        "right_censored": target is None,
    }
