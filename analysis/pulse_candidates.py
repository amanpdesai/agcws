"""Deterministic pulse-model proposals; predicted fits are never measured witnesses."""

import numpy as np


def basis(samples, completion, *, release=2048, baseline=2, stride=256):
    samples = np.asarray(samples, dtype=float)
    if samples.shape != (65536,) or not release < completion < 65536:
        raise ValueError("fixed-window single-job trace required")
    pulse = np.maximum(0, samples[release:completion] - baseline)
    prefix = np.concatenate(([0.0], np.cumsum(pulse)))
    positions = np.arange(release, 65536-len(pulse)+1, stride)
    edges = np.arange(9)*8192
    boundaries = np.clip(edges[None, :] - positions[:, None], 0, len(pulse))
    values = np.diff(prefix[boundaries], axis=1)/8192
    return positions, values, len(pulse)


def propose(target, samples, completion, *, pattern, seed, stride=256):
    """One candidate per job count; four initializations and three coordinate sweeps."""
    target = np.asarray(target, dtype=float)
    if target.shape != (8,) or not np.isfinite(target).all():
        raise ValueError("eight finite target bins required")
    if stride not in (16, 256):
        raise ValueError("versioned release grid must be 16 or 256 cycles")
    positions, values, duration = basis(samples, completion, stride=stride)
    rng = np.random.default_rng(seed)
    candidates = []
    for count in range(1, 9):
        best = None
        for restart in range(4):
            selected = []
            for _ in range(count):
                allowed = np.ones(len(positions), dtype=bool)
                for index in selected:
                    allowed &= np.abs(positions-positions[index]) >= duration
                choices = np.flatnonzero(allowed)
                if not len(choices):
                    break
                current = 2 + values[selected].sum(axis=0) if selected else np.full(8, 2.0)
                scores = ((current+values[choices]-target)**2).mean(axis=1)
                shortlist = choices[np.argsort(scores, kind="stable")[:min(8, len(choices))]]
                selected.append(int(shortlist[0] if restart == 0 else rng.choice(shortlist)))
            if len(selected) != count:
                continue
            for _ in range(3):
                for coordinate in range(count):
                    others = selected[:coordinate]+selected[coordinate+1:]
                    allowed = np.ones(len(positions), dtype=bool)
                    for index in others:
                        allowed &= np.abs(positions-positions[index]) >= duration
                    choices = np.flatnonzero(allowed)
                    current = 2+values[others].sum(axis=0) if others else np.full(8, 2.0)
                    scores = ((current+values[choices]-target)**2).mean(axis=1)
                    selected[coordinate] = int(choices[np.argmin(scores)])
            predicted = 2+values[selected].sum(axis=0)
            score = float(((predicted-target)**2).mean())
            starts = sorted(int(positions[index]) for index in selected)
            if best is None or (score, starts) < (best[0], best[1]):
                best = score, starts, predicted
        if best is not None:
            candidates.append({"program": {"size": 16, "pattern": pattern, "data_seed": 7500,
                                            "phases": [{"start": start, "duration": 1, "jobs": 1}
                                                       for start in best[1]]},
                               "predicted_rates": best[2].tolist(), "predicted_mse": best[0],
                               "qualified": False})
    return candidates
