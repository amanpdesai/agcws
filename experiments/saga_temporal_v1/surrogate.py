"""Order-aware features and fail-closed multi-output ridge regression."""

import json
import math

import numpy as np

from experiments.ibex_temporal_v1.program import BINARY
from experiments.ibex_temporal_v3.program import HORIZON, WORK, allocation, canonical

OPS = (*BINARY, "load", "store")
PHASE_WIDTH = 5 + len(OPS) + 3


def features(program):
    program = canonical(program)
    phases = program["segments"]
    result = [len(phases) / 8, program["memory_seed"] / (2**32 - 1)]
    for register in program["registers"]:
        result.extend(
            [register / (2**32 - 1), register.bit_count() / 32, float(register == 0)]
        )
    counts = allocation(program)
    for i, phase in enumerate(phases):
        body = phase["body"]
        result.extend(
            [
                1.0,
                phase["release"] / HORIZON,
                counts[i] / WORK,
                len(body) / 8,
                sum(counts[:i]) / WORK,
            ]
        )
        result.extend(sum(op["op"] == kind for op in body) / len(body) for kind in OPS)
        result.extend(
            [
                sum(op.get("dst") == op["a"] for op in body) / len(body),
                sum(op.get("dst") == op.get("b", -1) for op in body) / len(body),
                sum(op["a"] == op.get("b", -1) for op in body) / len(body),
            ]
        )
    result.extend([0.0] * PHASE_WIDTH * (8 - len(phases)))
    return np.asarray(result, dtype=np.float64)


def training_rows(history):
    if [t["slot"] for t in history] != list(range(1, len(history) + 1)):
        raise ValueError("complete ordered history required")
    rows, seen = [], set()
    for trial in history:
        if trial["status"] != "MEASURED" or not trial["valid"]:
            continue
        identity = json.dumps(canonical(trial["program"]), sort_keys=True)
        if identity not in seen:
            rows.append(trial)
            seen.add(identity)
    if len(rows) < 2:
        raise ValueError("at least two distinct valid measured programs required")
    return rows


class Ridge:
    def __init__(self, history, scale, alpha=1.0):
        if (
            not math.isfinite(scale)
            or scale <= 0
            or not math.isfinite(alpha)
            or alpha <= 0
        ):
            raise ValueError("positive finite scale and regularization required")
        rows = training_rows(history)
        x = np.stack([features(t["program"]) for t in rows])
        y = np.asarray([t["rates"] for t in rows], dtype=np.float64) / scale
        if y.shape != (len(rows), 8) or not np.isfinite(y).all() or (y < 0).any():
            raise ValueError("finite nonnegative measured eight-bin profiles required")
        self.training_slots = [t["slot"] for t in rows]
        self.x_mean, self.y_mean = x.mean(axis=0), y.mean(axis=0)
        self.x = x - self.x_mean
        self.weights = np.linalg.solve(
            self.x @ self.x.T + alpha * np.eye(len(rows)), y - self.y_mean
        )
        if not np.isfinite(self.weights).all():
            raise ValueError("nonfinite surrogate fit")
        self.scale = scale

    def predict(self, program):
        x = features(program) - self.x_mean
        prediction = (self.y_mean + x @ self.x.T @ self.weights) * self.scale
        if not np.isfinite(prediction).all():
            raise ValueError("nonfinite surrogate prediction")
        return prediction.tolist()

    def distance(self, program):
        x = features(program) - self.x_mean
        return float(np.min(np.sum((self.x - x) ** 2, axis=1)))


def screen(programs, history, target, scale):
    if (
        len(programs) != 4
        or len(target) != 8
        or not all(math.isfinite(v) and v >= 0 for v in target)
    ):
        raise ValueError(
            "four proposals and finite nonnegative eight-bin target required"
        )
    model = Ridge(history, scale)
    rates = [model.predict(p) for p in programs]
    losses = [
        math.sqrt(
            sum(((a - b) / scale) ** 2 for a, b in zip(r, target, strict=True)) / 8
        )
        for r in rates
    ]
    distances = [model.distance(p) for p in programs]
    best = min(range(4), key=lambda i: (losses[i], i))
    exploratory = min(
        (i for i in range(4) if i != best), key=lambda i: (-distances[i], i)
    )
    return {
        "selected_indices": sorted([best, exploratory]),
        "predicted_rates": rates,
        "predicted_losses": losses,
        "novelty_squared_distance": distances,
        "training_slots": model.training_slots,
    }
