"""Canonical weighted RV32IM language, allocation and architectural reference."""

import math
from itertools import cycle, islice, pairwise

import jsonschema

MASK = 2**32 - 1

WORK = 4096

HORIZON = 200000

REG = {"type": "integer", "minimum": 0, "maximum": 7}

BINARY = ("add", "xor", "and", "or", "sll", "srl", "mul", "divu", "cmovz")


def operation_schema(op, fields):
    return {
        "type": "object",
        "required": ["op", *fields],
        "properties": {"op": {"const": op}, **{k: REG for k in fields}},
        "additionalProperties": False,
    }


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["registers", "memory_seed", "segments"],
    "additionalProperties": False,
    "properties": {
        "registers": {
            "type": "array",
            "minItems": 8,
            "maxItems": 8,
            "items": {"type": "integer", "minimum": 0, "maximum": MASK},
        },
        "memory_seed": {"type": "integer", "minimum": 0, "maximum": MASK},
        "segments": {
            "type": "array",
            "minItems": 1,
            "maxItems": 8,
            "items": {
                "type": "object",
                "required": ["weight", "release", "body"],
                "additionalProperties": False,
                "properties": {
                    "release": {"type": "integer", "minimum": 0, "maximum": HORIZON},
                    "weight": {"type": "integer", "minimum": 1, "maximum": 4096},
                    "body": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 8,
                        "items": {
                            "oneOf": [
                                *[operation_schema(op, ("dst", "a", "b")) for op in BINARY],
                                operation_schema("load", ("dst", "a")),
                                operation_schema("store", ("a", "b")),
                            ]
                        },
                    },
                },
            },
        },
    },
}


def initial_memory(seed):
    return [seed + i * 2654435769 & MASK for i in range(64)]


def random_operation(rng, operations=None):
    op = rng.choice(operations or [*BINARY, "load", "store"])
    fields = ("a", "b") if op == "store" else ("dst", "a") if op == "load" else ("dst", "a", "b")
    return {"op": op, **{k: rng.randrange(8) for k in fields}}


def canonical(program):

    def numbers(value, path=()):
        if isinstance(value, dict):
            return {k: numbers(v, (*path, k)) for k, v in value.items()}
        if isinstance(value, list):
            return [numbers(v, (*path, i)) for i, v in enumerate(value)]
        if isinstance(value, float):
            if not math.isfinite(value):
                raise jsonschema.ValidationError("finite JSON numbers required", path=path)
            if value.is_integer():
                return int(value)
        return value

    result = numbers(program)
    jsonschema.Draft202012Validator(SCHEMA).validate(result)
    return result


def validate(program):
    canonical(program)


def allocate(weights):
    """Hamilton allocation, index tie-breaks, then a one-operation minimum."""
    if not 1 <= len(weights) <= 8 or any(type(w) is not int or not 1 <= w <= WORK for w in weights):
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


def allocation(program):
    program = canonical(program)
    return allocate([s["weight"] for s in program["segments"]])


def interpret(program):
    program = canonical(program)
    counts = allocation(program)
    regs, memory = (list(program["registers"]), initial_memory(program["memory_seed"]))
    operations = {}
    for segment, count in zip(program["segments"], counts):
        for inst in islice(cycle(segment["body"]), count):
            op, a = (inst["op"], regs[inst["a"]])
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
    n = rng.randint(1, 8)
    cuts = [0, *sorted(rng.sample(range(1, WORK // 8), n - 1)), WORK // 8]
    segments = []
    releases = sorted(rng.randrange(HORIZON * 9 // 10) for _ in range(n))
    for left, right in pairwise(cuts):
        size = rng.choice([1, 2, 4, 8])
        family = rng.choice(
            [
                None,
                ("divu",),
                ("mul",),
                ("load", "store"),
                ("add", "xor", "and", "or", "sll", "srl"),
                ("cmovz",),
            ]
        )
        body = [random_operation(rng, family) for _ in range(size)]
        if rng.random() < 0.5:
            for instruction in body:
                if "dst" in instruction:
                    instruction["dst"] = rng.randrange(2, 8)
                if "b" in instruction:
                    instruction["b"] = rng.choice([0, 1])
        segments.append(
            {
                "weight": (right - left) * 8,
                "release": releases[len(segments)],
                "body": body,
            }
        )
    return {
        "registers": [rng.choice([0, 1, 17, 31, MASK, rng.getrandbits(32)]) for _ in range(8)],
        "memory_seed": rng.getrandbits(32),
        "segments": segments,
    }


def mutate(program, rng):
    result = canonical(program)
    segments = result["segments"]
    segment = rng.choice(segments)
    kind = rng.randrange(10)
    if kind == 0:
        result["registers"][rng.randrange(8)] ^= 1 << rng.randrange(32)
    elif kind == 1:
        segment["weight"] = rng.randint(1, WORK)
    elif kind == 2:
        segment["release"] = rng.randrange(HORIZON)
    elif kind == 3:
        rng.shuffle(segments)
    elif kind == 4:
        segment["body"][rng.randrange(len(segment["body"]))] = random_operation(rng)
    elif kind == 5 and len(segment["body"]) < 8:
        segment["body"].insert(rng.randrange(len(segment["body"]) + 1), random_operation(rng))
    elif kind == 6 and len(segment["body"]) > 1:
        segment["body"].pop(rng.randrange(len(segment["body"])))
    elif kind == 7 and len(segments) < 8:
        segments.insert(
            rng.randrange(len(segments) + 1),
            {
                "weight": rng.randint(1, WORK),
                "release": rng.randrange(HORIZON),
                "body": [random_operation(rng) for _ in range(rng.randint(1, 8))],
            },
        )
    elif kind == 8 and len(segments) > 1:
        segments.pop(rng.randrange(len(segments)))
    else:
        result["memory_seed"] = rng.randrange(2**32)
    validate(result)
    return result
