"""Deterministic feasibility filter, independent of search outcomes."""

import math
import statistics

from experiments.ibex_temporal_v3.search import error


def select(witnesses, scale, count=3, minimum_floor=0.2, distance=0.15):
    if not math.isfinite(scale) or scale <= 0 or type(count) is not int or count < 1:
        raise ValueError("positive scale and target count required")
    selected = []
    for trial in witnesses:
        if not trial["valid"]:
            continue
        rates = trial["rates"]
        if len(rates) != 8 or any(not math.isfinite(x) or x < 0 for x in rates):
            raise ValueError("eight finite nonnegative rates required")
        floor = statistics.pstdev(rates) / scale
        if floor < minimum_floor or any(
            error(rates, t["rates"], scale) < distance for t in selected
        ):
            continue
        selected.append(
            {
                "id": f"target_{len(selected)}",
                "rates": rates,
                "constant_floor": floor,
                "witness_slot": trial["slot"],
                "witness_cache_id": trial["cache_id"],
            }
        )
        if len(selected) == count:
            return selected
    raise ValueError(
        f"qualification failed: {len(selected)}/{count} witnesses; no replacement draws"
    )
