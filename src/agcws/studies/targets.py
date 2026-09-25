"""Requested shapes independent of workload constructors; qualification is separate."""

import math
import statistics

SHAPES = {
    "activation": (0, 0, 1, 1, 1, 1, 1, 1),
    "deactivation": (1, 1, 1, 1, 0, 0, 0, 0),
    "burst": (0, 0, 0, 1, 1, 0, 0, 0),
    "quiet_interval": (1, 1, 1, 0, 0, 1, 1, 1),
    "alternating": (0, 1, 0, 1, 0, 1, 0, 1),
    "ramp": (0, 0, 0.33, 0.33, 0.67, 0.67, 1, 1),
    "rise_fall": (0, 0.5, 1, 1, 1, 0.5, 0, 0),
    "irregular": (0.5, 1, 0, 0, 1, 0.5, 0, 1),
    "flat_control": (0.5,) * 8,
}


def vector(values):
    if len(values) != 8 or any(
        type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in values
    ):
        raise ValueError("eight finite nonnegative rates required")
    return tuple(values)


def distance(left, right, scale):
    if type(scale) not in (int, float) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("positive finite fixed scale required")
    return math.sqrt(statistics.mean((a - b) ** 2 for a, b in zip(vector(left), vector(right)))) / scale


def diagnostics(rates, scale):
    values = vector(rates)
    mean = statistics.mean(values)
    return {
        "constant_floor": distance(values, [mean] * 8, scale),
        "best_constant_rate": mean,
        "span_over_scale": (max(values) - min(values)) / scale,
        "total_variation_over_scale": sum(abs(b - a) for a, b in zip(values, values[1:])) / scale,
    }


def requests(low, high, *, split):
    """Different amplitudes by split, fixed before witness searching.

    These are requests, not claims of feasibility or measured envelopes. The
    supplied endpoints must come from an independently frozen calibration.
    """
    if split not in ("development", "confirmation"):
        raise ValueError("explicit development/confirmation split required")
    vector([low, high] * 4)
    if high <= low:
        raise ValueError("nondegenerate calibration endpoints required")
    lower, upper = (0.2, 0.8) if split == "development" else (0.1, 0.9)
    result = []
    for name, pattern in SHAPES.items():
        shape = pattern
        if name == "flat_control":
            shape = (0.4 if split == "development" else 0.6,) * 8
        rates = [low + (high - low) * (lower + (upper - lower) * x) for x in shape]
        result.append({"id": name, "split": split, "rates": rates,
                       "control": name == "flat_control", "qualified": False,
                       **diagnostics(rates, high - low)})
    return result


def qualify(request, witness, *, scale, tolerance, nonflat_margin):
    """Fail closed on invalid witnesses; no replacing request by achieved rates."""
    if (not math.isfinite(tolerance) or tolerance <= 0
            or not math.isfinite(nonflat_margin) or nonflat_margin < 0):
        raise ValueError("positive tolerance and nonnegative margin required")
    reasons = []
    if witness["valid"] is not True:
        return {"qualified": False, "reasons": ["invalid_witness"], "witness_error": None}
    error = distance(request["rates"], witness["rates"], scale)
    floor = diagnostics(request["rates"], scale)["constant_floor"]
    if error > tolerance:
        reasons.append("witness_misses_request")
    if request["control"]:
        if floor > tolerance or diagnostics(witness["rates"], scale)["constant_floor"] > tolerance:
            reasons.append("control_not_near_flat")
    elif floor <= tolerance + nonflat_margin:
        reasons.append("insufficient_nonflat_floor")
    return {"qualified": not reasons, "reasons": reasons, "witness_error": error}


def mean_matched_requests(low, high, mean, *, split):
    """Preserve calibrated mean for exact-work contracts without using witnesses."""
    if split not in ("development", "confirmation"):
        raise ValueError("explicit development/confirmation split required")
    vector([low, high, mean, low, high, mean, low, high])
    if not low < mean < high:
        raise ValueError("calibrated mean must lie strictly inside endpoints")
    fraction = 0.75 if split == "development" else 0.9
    result = []
    for name, shape in SHAPES.items():
        center = statistics.mean(shape)
        if name == "flat_control":
            rates = [mean]*8
        else:
            amplitude = fraction * min((mean-low)/(center-min(shape)),
                                       (high-mean)/(max(shape)-center))
            rates = [mean + amplitude*(value-center) for value in shape]
        result.append({"id": name, "split": split, "rates": rates,
                       "control": name == "flat_control", "qualified": False,
                       "normalization": "calibration-mean-preserving",
                       **diagnostics(rates, high-low)})
    return result
