"""Profile-guided timing search; PaTGen/SAGA-inspired, not a reproduction."""

import copy
import hashlib
import json

import numpy as np

from agcws.pipeline.ibex.program import HORIZON, canonical
from agcws.pipeline.metrics import key
from agcws.workloads.schedule import expand_schedule

VERSION = "phase-model-v1"
POOL = 32
RIDGE = 0.1


def features(program, design):
    """Bounded temporal occupancy descriptors, not a physical power model."""
    bins = np.zeros((8, 4))
    if "sequence" in program:
        sequence = expand_schedule(program, design.contract)
        horizon = design.clock_edges
        work_cycles = (horizon - design.contract.idle_cycles) / design.contract.work_units
        position, phases = 0.0, []
        for node in sequence:
            duration = node["cycles"] if node["op"] == "wait" else node["units"] * work_cycles
            if node["op"] == "work":
                phases.append((position, duration, node["units"] / design.contract.work_units, "work"))
            position += duration
    elif "segments" in program:
        horizon = HORIZON
        total = sum(s["weight"] for s in program["segments"])
        phases = [(s["release"], horizon * s["weight"] / total / 4,
                   s["weight"] / total, json.dumps(s["body"], sort_keys=True)) for s in program["segments"]]
    elif "phases" in program:
        horizon = design.clock_edges
        phases = [(p["start"], p["duration"], p.get("jobs", p.get("packets", 1)) / 512,
                   json.dumps({k: v for k, v in p.items() if k not in ("start", "duration")}, sort_keys=True))
                  for p in program["phases"]]
    else:
        raise ValueError("unsupported temporal representation")
    for start, duration, mass, kind in phases:
        category = int(hashlib.sha256(kind.encode()).hexdigest()[:8], 16) % 3 + 1
        for index in range(8):
            overlap = max(0, min(start + duration, (index + 1) * horizon / 8) - max(start, index * horizon / 8))
            bins[index, 0] += overlap / (horizon / 8)
            bins[index, category] += mass * overlap / max(duration, 1)
    return np.concatenate(([1.0], np.tanh(bins.flatten())))


def timing_edit(program, design, rng):
    child = copy.deepcopy(program)
    if "sequence" in child:
        child = {"sequence": expand_schedule(child, design.contract)}
        field = rng.choice(["cycles", "units"])
        nodes = [n for n in child["sequence"] if field in n]
        if len(nodes) >= 2:
            donor, receiver = rng.sample(nodes, 2)
            maximum = 10000 if field == "cycles" else 256
            amount = min(donor[field] - 1, maximum - receiver[field],
                         max(1, donor[field] // rng.choice([2, 4, 8, 16])))
            donor[field] -= amount
            receiver[field] += amount
        else:
            rng.shuffle(child["sequence"])
    elif "segments" in child:
        node = rng.choice(child["segments"])
        step = rng.choice([HORIZON // 128, HORIZON // 64, HORIZON // 16])
        node["release"] = max(0, min(HORIZON, node["release"] + rng.choice([-step, step])))
        child = canonical(child)
    elif "phases" in child:
        node = rng.choice(child["phases"])
        step = max(1, design.clock_edges // rng.choice([16, 64, 128]))
        field = rng.choice(["start", "duration"])
        maximum = design.clock_edges - node["duration" if field == "start" else "start"]
        node[field] = max(0 if field == "start" else 1,
                          min(maximum, node[field] + rng.choice([-step, step])))
    else:
        raise ValueError("unsupported temporal representation")
    return child


def propose(design, rng, slot, history):
    if type(slot) is not int or slot <= len(history) or [t["slot"] for t in history] != list(range(1, len(history) + 1)):
        raise ValueError("ordered, strictly earlier history required")
    valid = [t for t in history if t["valid"] is True]
    if any(len(t["residual"]) != 8 or not np.isfinite(t["residual"]).all() for t in valid):
        raise ValueError("finite eight-bin measured residuals required")
    note = {"version": VERSION, "slot": slot, "training_slots": [t["slot"] for t in valid],
            "internal_surrogate_candidates": 0, "extra_simulations": 0}
    if len(valid) < 8 or slot % 8 == 0:
        program, parents = design.propose_classical("phase-random", rng, slot, history)
        return program, parents, {**note, "mode": "bootstrap" if len(valid) < 8 else "immigrant"}
    ranked = sorted(valid, key=lambda t: (max(map(abs, t["residual"])), t["loss"], t["slot"]))
    # Structural offspring use the existing representation-specific GA, with max-bin selection.
    selection = [{**t, "loss": max(map(abs, t["residual"]))} if t["valid"] else t for t in history]
    pool, seen = [], {key(t["program"]) for t in history}
    for index in range(POOL):
        if index % 4 == 0:
            candidate, parents = design.propose_classical("phase-ga", rng, slot, selection)
        else:
            parent = ranked[index % min(8, len(ranked))]
            candidate = timing_edit(parent["program"], design, rng)
            parents = [parent["slot"]]
        identity = key(candidate)
        if identity not in seen:
            pool.append((candidate, parents))
            seen.add(identity)
    if not pool:
        # A recorded exploration branch for an exhausted local neighborhood, not an error fallback.
        program, parents = design.propose_classical("phase-random", rng, slot, history)
        return program, parents, {**note, "mode": "exhausted-neighborhood", "internal_surrogate_candidates": POOL}
    x = np.asarray([features(t["program"], design) for t in valid])
    y = np.asarray([t["residual"] for t in valid])
    penalty = np.eye(x.shape[1]) * RIDGE
    penalty[0, 0] = 1e-8
    coefficients = np.linalg.solve(x.T @ x + penalty, x.T @ y)
    options = np.asarray([features(p, design) for p, _ in pool])
    predictions = options @ coefficients
    distance = np.min(np.linalg.norm(options[:, None, :] - x[None, :, :], axis=2), axis=1)
    # Penalize extrapolation; periodic immigrants supply exploration explicitly.
    scores = np.max(np.abs(predictions), axis=1) + 0.05 * distance
    chosen = int(np.argmin(scores))
    program, parents = pool[chosen]
    return program, parents, {**note, "mode": "ridge-timing-refinement",
        "internal_surrogate_candidates": POOL, "distinct_candidates": len(pool),
        "predicted_residual": predictions[chosen].tolist(), "selected_score": float(scores[chosen]),
        "ridge": RIDGE, "selected_sha256": key(program)}
