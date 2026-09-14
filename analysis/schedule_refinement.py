"""Resource-conserving proposals for fixed-work witness qualification."""

import copy
import itertools
import random

from agcws.workloads.schedule import expand_schedule


def paired_transfer(program, contract, batch, seed):
    """Move work or idle between two positions; never repair rejected proposals."""
    if type(batch) is not int or not 0 <= batch < 128:
        raise ValueError("batch must be in [0,128)")
    sequence = expand_schedule(program, contract)
    coordinates = [(i, j, "units" if sequence[i]["op"] == "work" else "cycles")
                   for i, j in itertools.combinations(range(len(sequence)), 2)
                   if sequence[i]["op"] == sequence[j]["op"]]
    if not coordinates:
        raise ValueError("at least two work or two wait positions required")
    random.Random(seed + batch // len(coordinates)).shuffle(coordinates)
    left, right, field = coordinates[batch % len(coordinates)]
    step = (256 if batch < 16 else 64 if batch < 32 else
            16 if batch < 64 else 4 if batch < 96 else 1)
    if field == "units":
        step = 1
    candidates = []
    for sign in (-1, 1):
        edited = copy.deepcopy(sequence)
        edited[left][field] += sign * step
        edited[right][field] -= sign * step
        candidates.append({"sequence": edited})
    return candidates
