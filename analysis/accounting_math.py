"""Independent arithmetic for the frozen confirmation audit; no experiment imports."""

import math
import random


def rms(rates, target, scale):
    if len(rates) != 8 or len(target) != 8 or not math.isfinite(scale) or scale <= 0:
        raise ValueError("eight bins and positive finite scale required")
    if not all(math.isfinite(x) for x in [*rates, *target]):
        raise ValueError("nonfinite measurement")
    return math.sqrt(math.fsum((a - b) ** 2 for a, b in zip(rates, target)) / 8) / scale


def prefix(rows, budget, tolerance):
    if budget < 2:
        raise ValueError("at least two proposal indices required for AUC")
    rows = rows[:budget]
    if len(rows) != budget or [r["slot"] for r in rows] != list(range(1, budget + 1)):
        raise ValueError("incomplete proposal prefix")
    current = None
    curve, successes = [], []
    valid = 0
    for row in rows:
        value = row["loss"]
        if row["valid"]:
            if value is None or not math.isfinite(value) or value < 0:
                raise ValueError("invalid numeric loss")
            valid += 1
            current = value if current is None else min(current, value)
            if value <= tolerance:
                successes.append(row["slot"])
        elif value is not None:
            raise ValueError("rejected candidate received a score")
        curve.append(1.0 if current is None else current)
    # Trapezoid weights on x=1..N; there is no extra slot-zero interval.
    area = math.fsum(curve) - (curve[0] + curve[-1]) / 2
    return {
        "budget": budget,
        "auc": area,
        "mean_auc": area / (budget - 1),
        "curve": curve,
        "final_loss": current,
        "solved": bool(successes),
        "evaluations_to_target": min(successes) if successes else budget,
        "right_censored": not successes,
        "valid_slots": valid,
    }


def paired(differences):
    if len(differences) != 6 or not all(math.isfinite(v) for v in differences):
        raise ValueError("six finite seed units required")
    observed = math.fsum(differences) / 6
    extreme = 0
    for mask in range(64):
        value = math.fsum(d if mask & (1 << i) else -d for i, d in enumerate(differences)) / 6
        extreme += abs(value) >= abs(observed) - 1e-12
    rng = random.Random(1300)
    bootstrap = sorted(
        math.fsum(differences[int(rng.random() * 6)] for _ in range(6)) / 6 for _ in range(10000)
    )
    return {
        "mean_difference": observed,
        "seed_differences": differences,
        "two_sided_exact_sign_flip_p": extreme / 64,
        "seed_bootstrap_95_percentile": [bootstrap[249], bootstrap[9749]],
    }


def charge(response, reservation):
    if response["usage_unknown"]:
        if any(response[k] is not None for k in ("tokens_in", "tokens_out", "estimated_usd")):
            raise ValueError("unknown usage recorded as known")
        return {"known": 0.0, "reserved": reservation, "input": 0, "output": 0}
    fields = response["usage_fields"]
    counts = [
        fields[k] for k in ("prompt_token_count", "candidates_token_count", "thoughts_token_count")
    ]
    if any(type(x) is not int or x < 0 for x in counts):
        raise ValueError("invalid token count")
    incoming, output, thinking = counts
    if incoming > 200000:
        raise ValueError("frozen short-context pricing tier exceeded")
    if (response["tokens_in"], response["tokens_out"], response["thinking_tokens"]) != (
        incoming,
        output + thinking,
        thinking,
    ):
        raise ValueError("token aggregation differs")
    return {
        "known": (incoming * 1.25 + (output + thinking) * 10) / 1e6,
        "reserved": 0.0,
        "input": incoming,
        "output": output + thinking,
    }
