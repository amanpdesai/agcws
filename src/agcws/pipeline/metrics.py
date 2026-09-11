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


def summarize(history, budget, tolerance):
    rows = history[:budget]
    if len(rows) != budget or [t["slot"] for t in rows] != list(range(1, budget + 1)):
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
    solved = next((t["slot"] for t in rows if t["valid"] and t["loss"] <= tolerance), None)
    auc = sum(((a + b) / 2 for a, b in pairwise(curve)))
    return {
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
