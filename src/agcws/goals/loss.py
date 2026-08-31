"""Deterministic goal losses shared by every search policy."""
from __future__ import annotations

import math
from collections.abc import Sequence

from agcws.goals.schema import CompositionalGoal, ScalarGoal, TemporalGoal
from agcws.nodes.power import PowerProfile


def scalar_loss(profile: PowerProfile, goal: ScalarGoal, p_min: float, p_max: float) -> float:
    if p_max <= p_min:
        raise ValueError("power envelope must have positive width")
    q = (profile.mean_power - p_min) / (p_max - p_min)
    return abs(q - goal.q)


def temporal_loss(profile: PowerProfile, goal: TemporalGoal) -> float:
    observed = profile.windowed
    if observed is None or len(observed) != goal.windows:
        raise ValueError("profile window count does not match temporal goal")
    if not observed:
        raise ValueError("temporal profile cannot be empty")
    scale = max(max(observed), 1e-12)
    normalized = [value / scale for value in observed]
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(normalized, goal.profile)) / len(observed))


def compositional_loss(profile: PowerProfile, goal: CompositionalGoal, lam: float = 1.0) -> float:
    if profile.by_region is None:
        raise ValueError("profile has no regional attribution")
    total = sum(profile.by_region.values())
    if total <= 0:
        raise ValueError("regional power total must be positive")
    share_error = sum(abs(profile.by_region.get(region, 0.0) / total - target)
                      for region, target in goal.shares.items())
    return share_error + lam * max(0.0, goal.power_floor - profile.mean_power)


def loss(profile: PowerProfile, goal, *, p_min: float | None = None, p_max: float | None = None) -> float:
    if isinstance(goal, ScalarGoal):
        if p_min is None or p_max is None:
            raise ValueError("scalar loss requires an empirical envelope")
        return scalar_loss(profile, goal, p_min, p_max)
    if isinstance(goal, TemporalGoal):
        return temporal_loss(profile, goal)
    if isinstance(goal, CompositionalGoal):
        return compositional_loss(profile, goal)
    raise TypeError(f"unsupported goal type: {type(goal).__name__}")
