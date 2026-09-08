"""Weighted work allocation with explicit partial-iteration semantics."""

import copy
from itertools import cycle, islice

import jsonschema

from experiments.ibex_temporal_v1 import program as v1

WORK, HORIZON, MASK = v1.WORK, v1.HORIZON, v1.MASK
SCHEMA = copy.deepcopy(v1.SCHEMA)
segment_schema = SCHEMA["properties"]["segments"]["items"]
segment_schema["required"] = ["weight", "release", "body"]
del segment_schema["properties"]["iterations"]
segment_schema["properties"]["weight"] = {
    "type": "integer",
    "minimum": 1,
    "maximum": WORK,
}


def allocate(weights):
    """Hamilton allocation, index tie-breaks, then a one-operation minimum."""
    if not 1 <= len(weights) <= 8 or any(
        type(w) is not int or not 1 <= w <= WORK for w in weights
    ):
        raise ValueError("one to eight integer weights in [1,4096] required")
    total = sum(weights)
    counts = [WORK * w // total for w in weights]
    order = sorted(range(len(weights)), key=lambda i: (-(WORK * weights[i] % total), i))
    for i in order[: WORK - sum(counts)]:
        counts[i] += 1
    for i in range(len(counts)):
        if counts[i] == 0:
            donor = max(range(len(counts)), key=lambda j: (counts[j], -j))
            counts[donor] -= 1
            counts[i] = 1
    assert sum(counts) == WORK and min(counts) > 0
    return counts


def validate(program):
    jsonschema.Draft202012Validator(SCHEMA).validate(program)


def allocation(program):
    validate(program)
    return allocate([s["weight"] for s in program["segments"]])


def from_v1(program):
    v1.validate(program)
    result = copy.deepcopy(program)
    for segment in result["segments"]:
        segment["weight"] = segment.pop("iterations") * len(segment["body"])
    assert allocation(result) == [
        s["iterations"] * len(s["body"]) for s in program["segments"]
    ]
    return result


def interpret(program):
    counts = allocation(program)
    regs, memory = list(program["registers"]), v1.initial_memory(program["memory_seed"])
    operations = {}
    for segment, count in zip(program["segments"], counts):
        for inst in islice(cycle(segment["body"]), count):
            op, a = inst["op"], regs[inst["a"]]
            b = regs[inst["b"]] if "b" in inst else 0
            operations[op] = operations.get(op, 0) + 1
            if op == "store":
                memory[a & 63] = b
                continue
            if op == "load":
                value = memory[a & 63]
            elif op == "add":
                value = a + b
            elif op == "xor":
                value = a ^ b
            elif op == "and":
                value = a & b
            elif op == "or":
                value = a | b
            elif op == "sll":
                value = a << (b & 31)
            elif op == "srl":
                value = a >> (b & 31)
            elif op == "mul":
                value = a * b
            elif op == "divu":
                value = MASK if b == 0 else a // b
            elif op == "cmovz":
                value = b if a == 0 else regs[inst["dst"]]
            else:
                raise ValueError(op)
            regs[inst["dst"]] = value & MASK
    return {
        "registers": regs,
        "memory": memory,
        "operations": operations,
        "useful_work": sum(operations.values()),
        "allocation": counts,
    }


def random_program(rng):
    return from_v1(v1.random_program(rng))


def mutate(program, rng):
    result = copy.deepcopy(program)
    if rng.random() < 0.2:
        return random_program(rng)
    kind = rng.randrange(5)
    segment = rng.choice(result["segments"])
    if kind == 0:
        result["registers"][rng.randrange(8)] ^= 1 << rng.randrange(32)
    elif kind == 1:
        segment["weight"] = rng.randint(1, WORK)
    elif kind == 2:
        segment["release"] = rng.randrange(HORIZON)
    elif kind == 3:
        rng.shuffle(result["segments"])
    else:
        segment["body"][rng.randrange(len(segment["body"]))] = v1.random_operation(rng)
    validate(result)
    return result
