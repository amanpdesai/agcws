"""Resource-conserving proposals for fixed-work witness qualification."""

import copy
import itertools
import math
import random

from agcws.workloads.schedule import expand_schedule


def allocate(total, weights):
    if not weights or any(not math.isfinite(w) or w < 0 for w in weights) or sum(weights) <= 0:
        raise ValueError("finite nonnegative allocation weights required")
    exact = [total*w/sum(weights) for w in weights]
    values = [math.floor(v) for v in exact]
    order = sorted(range(len(values)), key=lambda i: (-(exact[i]-values[i]), i))
    for i in order[:total-sum(values)]:
        values[i] += 1
    return values


def initial_schedules(rates, baseline, contract, edges):
    """Three explicitly measured proposals, not inferred feasible witnesses."""
    if len(rates) != 8 or edges <= contract.idle_cycles:
        raise ValueError("eight bins and positive estimated active duration required")
    work = allocate(contract.work_units, [max(0, r-baseline) for r in rates])
    unit_cycles = (edges-contract.idle_cycles)/contract.work_units
    waits = allocate(contract.idle_cycles, [max(0, edges/8-w*unit_cycles) for w in work])
    candidates = []
    for lead in (0, .5, 1):
        sequence = []
        for units, cycles in zip(work, waits, strict=True):
            before = int(cycles*lead)
            if before:
                sequence.append({"op": "wait", "cycles": before})
            if units:
                sequence.append({"op": "work", "units": units})
            if cycles-before:
                sequence.append({"op": "wait", "cycles": cycles-before})
        candidate = {"sequence": sequence}
        expand_schedule(candidate, contract)
        candidates.append(candidate)
    return candidates


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
