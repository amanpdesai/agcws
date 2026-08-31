"""Pre-declared calibration rules for experiment parameters."""
from __future__ import annotations

import math
from statistics import quantiles


def choose_scalar_epsilon(solved_fraction: float, base: float = 0.05) -> float:
    """Apply the one-adjustment rule declared in EXPERIMENTS.md."""
    if not 0.0 <= solved_fraction <= 1.0:
        raise ValueError("solved_fraction must be in [0,1]")
    if solved_fraction > 0.6:
        return 0.02
    if solved_fraction < 0.1:
        return 0.10
    return base


def tenth_percentile(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot calculate percentile of empty corpus")
    if len(values) == 1:
        return values[0]
    return quantiles(values, n=10, method="inclusive")[0]


def calibration_record(records: list[dict], solved_fraction: float | None = None) -> dict:
    if not records:
        raise ValueError("calibration corpus is empty")
    valid = [record for record in records if record.get("valid", True)]
    proxy = [float(record["activity"]["total_transitions"]) /
             max(1, int(record["activity"]["clock_edges"])) for record in valid
             if "activity" in record]
    powers = proxy or [float(record["mean_power"]) for record in valid]
    work = [float(record["useful_work"]) for record in records if record.get("valid", True)]
    if not powers or not work:
        raise ValueError("corpus has no valid measurements")
    result = {"count": len(records), "valid_count": len(powers),
              "power_metric": "total_transitions_per_clock_edge" if proxy else "mean_power",
              "p_min": min(powers), "p_max": max(powers),
              "useful_work_floor": math.floor(tenth_percentile(work)),
              "epsilon_scalar": choose_scalar_epsilon(solved_fraction)
              if solved_fraction is not None else 0.05,
              "epsilon_rule": ">0.6 -> 0.02; <0.1 -> 0.10; otherwise 0.05"}
    if solved_fraction is not None:
        result["random_solved_fraction"] = solved_fraction
    else:
        result["random_solved_fraction"] = None
        result["status"] = "provisional_until_random_search_outcomes"
    return result
