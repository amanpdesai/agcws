"""Bounded paired local edits for measured witness qualification."""

import copy
import random


def pair(program, batch, seed):
    coordinates = [(i, field) for i, phase in enumerate(program["phases"])
                   for field in ("start", "duration", "jobs", "packets") if field in phase
                   and not (field == "duration" and phase.get("jobs") == 1)]
    if not coordinates or not 0 <= batch < 128:
        raise ValueError("phase coordinates and batch in [0,128) required")
    random.Random(seed+batch//len(coordinates)).shuffle(coordinates)
    index, field = coordinates[batch % len(coordinates)]
    step = 256 if batch < 16 else 64 if batch < 32 else 16 if batch < 64 else 4 if batch < 96 else 1
    if field in ("jobs", "packets"):
        step = 1
    candidates = []
    for sign in (-1, 1):
        candidate = copy.deepcopy(program)
        candidate["phases"][index][field] += sign*step
        candidates.append(candidate)
    return candidates
