"""Proposal-axis metrics and fixed-scale rate error."""

import hashlib
import json
import math
from itertools import pairwise


def key(program):
    return hashlib.sha256(json.dumps(program, sort_keys=True).encode()).hexdigest()


def error(rates, target, scale):
    if len(rates) != 8 or len(target) != 8 or scale <= 0:
        raise ValueError("eight bins and a positive frozen scale required")
    return math.sqrt(sum(((a - b) ** 2 for a, b in zip(rates, target))) / 8) / scale


def max_bin_error(rates, target, scale):
    if (len(rates) != 8 or len(target) != 8 or not math.isfinite(scale) or scale <= 0
            or any(not math.isfinite(x) for x in [*rates, *target])):
        raise ValueError("eight finite bins and positive scale required")
    return max(abs(a-b)/scale for a, b in zip(rates, target))


def success(trial, tolerance, metric="nrmse"):
    if metric not in ("nrmse", "max-bin"):
        raise ValueError("unknown success metric")
    if trial["valid"] is not True:
        return False
    value = trial["max_bin_error"] if metric == "max-bin" else trial["loss"]
    if value is None or not math.isfinite(value) or value < 0:
        raise ValueError("valid finite success error required")
    return value <= tolerance


def summarize(history, budget, tolerance, *, stop_on_success=False, success_metric="nrmse"):
    rows = history[:budget]
    if budget < 2 or not rows or [t["slot"] for t in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("complete ordered prefix required")
    if len(rows) != budget and not stop_on_success:
        raise ValueError("complete ordered prefix required")
    best, curve = (1.0, [])
    has_valid = False
    for trial in rows:
        loss = trial["loss"]
        if trial["valid"]:
            if loss is None or not math.isfinite(loss) or loss < 0:
                raise ValueError("valid finite loss required")
            best = min(best, loss) if has_valid else loss
            has_valid = True
        elif loss is not None:
            raise ValueError("invalid workload must not have a score")
        curve.append(best)
    solved = next((t["slot"] for t in rows if success(t, tolerance, success_metric)), None)
    if len(rows) < budget:
        if solved is None:
            raise ValueError("short trajectory requires a valid tolerance hit")
        curve.extend([best] * (budget - len(rows)))
    auc = sum(((a + b) / 2 for a, b in pairwise(curve)))
    result = {
        "budget": budget,
        "auc": auc,
        "mean_auc": auc / (budget - 1),
        "curve": curve,
        "final_loss": best if has_valid else None,
        "solved": solved is not None,
        "evaluations_to_target": solved if solved else budget,
        "right_censored": solved is None,
        "valid_slots": sum(t["valid"] for t in rows),
    }
    if stop_on_success:
        result.update(
            charged_slots=len(rows),
            stopped_early=len(rows) < budget,
            auc_completion="terminal_best_carried_forward",
        )
    if success_metric == "max-bin":
        result.update(success_metric=success_metric, auc_metric="nrmse",
                      best_max_bin_error=min((t["max_bin_error"] for t in rows if t["valid"]), default=None))
    return result
