"""Independent, achieved-target witnesses; never supplied to search policies."""

import argparse
import json
from pathlib import Path

from experiments.ibex_temporal_v1.program import validate

FAMILIES = {
    "logic": [
        {"op": op, "dst": i, "a": i, "b": 1}
        for i, op in zip((2, 3, 4, 5), ("and", "or", "sll", "srl"))
    ],
    "alu": [{"op": "xor", "dst": i, "a": i, "b": 1} for i in (2, 3, 4, 5)],
    "multiply": [{"op": "mul", "dst": i, "a": i, "b": 1} for i in (2, 3, 4, 5)],
    "divide": [{"op": "divu", "dst": i, "a": i, "b": 1} for i in (2, 3, 4, 5)],
    "zero_divide": [{"op": "divu", "dst": i, "a": i, "b": 0} for i in (2, 3, 4, 5)],
    "memory": [
        {"op": "store", "a": 2, "b": 3},
        {"op": "load", "dst": 4, "a": 2},
        {"op": "add", "dst": 2, "a": 2, "b": 1},
        {"op": "xor", "dst": 3, "a": 3, "b": 4},
    ],
    "branch": [
        {"op": "cmovz", "dst": 2, "a": 0, "b": 1},
        {"op": "cmovz", "dst": 3, "a": 2, "b": 1},
        {"op": "xor", "dst": 2, "a": 2, "b": 1},
        {"op": "cmovz", "dst": 4, "a": 2, "b": 3},
    ],
}

PATTERNS = {
    "target_0": ["alu", "alu", "divide", "divide", "divide", "divide", "alu", "alu"],
    "target_1": ["memory", "alu"] * 4,
    "target_2": ["multiply", "zero_divide", "divide", "branch"] * 2,
    "target_3": [
        "branch",
        "memory",
        "alu",
        "multiply",
        "branch",
        "divide",
        "zero_divide",
        "memory",
    ],
    "check_all": list(FAMILIES) + ["divide"],
}


def witness(name):
    program = {
        "registers": [0, 17, 0xFEDCBA98, 0x13579BDF, 0xAAAAAAAA, 0x55555555, 7, 31],
        "memory_seed": 0x12345678,
        "segments": [
            {"release": i * 25000, "iterations": 128, "body": FAMILIES[family]}
            for i, family in enumerate(PATTERNS[name])
        ],
    }
    validate(program)
    return program


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name in PATTERNS:
        (args.out / f"{name}.json").write_text(
            json.dumps(witness(name), indent=2) + "\n"
        )
