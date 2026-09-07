"""Shared JSON-number semantics; the frozen v2 language and work limits remain."""

import math

import jsonschema

from experiments.ibex_temporal_v1.program import random_operation
from experiments.ibex_temporal_v2 import program as v2
from experiments.ibex_temporal_v2.compiler import assembly as v2_assembly

SCHEMA, WORK, HORIZON = v2.SCHEMA, v2.WORK, v2.HORIZON


def canonical(program):
    def numbers(value, path=()):
        if isinstance(value, dict):
            return {k: numbers(v, (*path, k)) for k, v in value.items()}
        if isinstance(value, list):
            return [numbers(v, (*path, i)) for i, v in enumerate(value)]
        if isinstance(value, float):
            if not math.isfinite(value):
                raise jsonschema.ValidationError(
                    "finite JSON numbers required", path=path
                )
            if value.is_integer():
                return int(value)
        return value

    result = numbers(program)
    v2.validate(result)
    return result


def validate(program):
    canonical(program)


def allocation(program):
    return v2.allocation(canonical(program))


def interpret(program):
    return v2.interpret(canonical(program))


def assembly(program):
    return v2_assembly(canonical(program))


def random_program(rng):
    return v2.random_program(rng)


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
        segment["body"].insert(
            rng.randrange(len(segment["body"]) + 1), random_operation(rng)
        )
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
