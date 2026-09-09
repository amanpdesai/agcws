"""Phase-aware CPU controls; adaptations, not reproductions of GeST or SAGA."""

import copy
import math

from experiments.ibex_temporal_v1.program import BINARY, random_operation
from experiments.ibex_temporal_v3.program import HORIZON, WORK, canonical

FAMILIES = (
    ("divu",),
    ("mul",),
    ("load", "store"),
    ("cmovz",),
    ("add", "xor", "and", "or", "sll", "srl"),
    (*BINARY, "load", "store"),
)


def phase_random(rng, slot):
    if type(slot) is not int or slot < 1:
        raise ValueError("positive proposal index required")
    n = 1 + (slot - 1) % 8
    # Stratify phase counts, independently sample work weights and bounded release cells.
    segments = []
    for i in range(n):
        family = rng.choice(FAMILIES)
        body = [random_operation(rng, family) for _ in range(rng.randint(1, 8))]
        if rng.random() < 0.5:
            for op in body:
                if "dst" in op:
                    op["dst"] = rng.randrange(2, 8)
                if "b" in op:
                    op["b"] = rng.randrange(2)
        segments.append(
            {
                "weight": rng.randint(1, WORK),
                "release": rng.randrange(
                    i * HORIZON * 3 // (4 * n), (i + 1) * HORIZON * 3 // (4 * n)
                ),
                "body": body,
            }
        )
    return canonical(
        {
            "registers": [
                rng.choice([0, 1, 17, 31, 2**32 - 1, rng.getrandbits(32)])
                for _ in range(8)
            ],
            "memory_seed": rng.getrandbits(32),
            "segments": segments,
        }
    )


def mutate(program, rng):
    result = copy.deepcopy(canonical(program))
    segments = result["segments"]
    segment = rng.choice(segments)
    operators = ["release", "weight", "instruction", "register", "swap", "mix"]
    if len(segments) < 8:
        operators.append("insert")
    if len(segments) > 1:
        operators.append("delete")
    operator = rng.choice(operators)
    if operator == "release":
        segment["release"] = (
            segment["release"]
            + rng.choice([-1, 1])
            * rng.choice([HORIZON // 32, HORIZON // 8, HORIZON // 2])
        ) % HORIZON
    elif operator == "weight":
        segment["weight"] = rng.randint(1, WORK)
    elif operator == "instruction":
        segment["body"][rng.randrange(len(segment["body"]))] = random_operation(rng)
    elif operator == "register":
        result["registers"][rng.randrange(8)] ^= 1 << rng.randrange(32)
    elif operator == "swap":
        rng.shuffle(segments)
    elif operator == "mix":
        family = rng.choice(FAMILIES)
        segment["body"] = [
            random_operation(rng, family) for _ in range(rng.randint(1, 8))
        ]
    elif operator == "insert":
        segments.insert(
            rng.randrange(len(segments) + 1),
            {
                "weight": rng.randint(1, WORK),
                "release": rng.randrange(HORIZON),
                "body": [random_operation(rng) for _ in range(rng.randint(1, 8))],
            },
        )
    elif operator == "delete":
        segments.pop(rng.randrange(len(segments)))
    else:
        raise ValueError(operator)
    return canonical(result), operator


def phase_ga(rng, slot, history):
    if [t["slot"] for t in history] != list(range(1, len(history) + 1)) or slot <= len(
        history
    ):
        raise ValueError("ordered, strictly earlier history required")
    valid = [t for t in history if t["valid"]]
    if any(t["loss"] is None or not math.isfinite(t["loss"]) for t in valid):
        raise ValueError("valid history needs finite measured losses")
    # An explicit bootstrap/immigration schedule, not an exception-driven fallback.
    if len(valid) < 4 or slot % 8 == 0:
        return phase_random(rng, slot), {
            "operator": "bootstrap" if len(valid) < 4 else "immigrant",
            "parents": [],
        }
    elite = sorted(valid, key=lambda t: (t["loss"], t["slot"]))[:8]
    parents = [
        min(rng.sample(elite, 2), key=lambda t: (t["loss"], t["slot"]))
        for _ in range(2)
    ]
    left = copy.deepcopy(parents[0]["canonical_program"])
    right = parents[1]["canonical_program"]
    a = rng.randint(1, len(left["segments"]))
    b = rng.randrange(len(right["segments"]))
    # Choose a legal suffix length explicitly; do not truncate an invalid offspring.
    count = rng.randint(0, min(8 - a, len(right["segments"]) - b))
    left["segments"] = left["segments"][:a] + copy.deepcopy(
        right["segments"][b : b + count]
    )
    for i in range(8):
        if rng.random() < 0.5:
            left["registers"][i] = right["registers"][i]
    child, operator = mutate(left, rng)
    return child, {
        "operator": "crossover+" + operator,
        "parents": [t["slot"] for t in parents],
    }
