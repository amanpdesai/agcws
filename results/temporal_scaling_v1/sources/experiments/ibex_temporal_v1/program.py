"""Bounded RV32IM programs with an independent architectural interpreter."""

import copy
import json
import random
from itertools import pairwise

import jsonschema

MASK = 2**32 - 1
WORK = 4096
HORIZON = 200_000
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
                "required": ["iterations", "release", "body"],
                "additionalProperties": False,
                "properties": {
                    "release": {"type": "integer", "minimum": 0, "maximum": HORIZON},
                    "iterations": {"type": "integer", "minimum": 1, "maximum": 4096},
                    "body": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 8,
                        "items": {
                            "oneOf": [
                                *[
                                    operation_schema(op, ("dst", "a", "b"))
                                    for op in BINARY
                                ],
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


def validate(program):
    jsonschema.Draft202012Validator(SCHEMA).validate(program)
    work = sum(s["iterations"] * len(s["body"]) for s in program["segments"])
    if work != WORK:
        raise ValueError(f"semantic body operations must total {WORK}, got {work}")


def initial_memory(seed):
    return [(seed + i * 0x9E3779B9) & MASK for i in range(64)]


def interpret(program):
    validate(program)
    regs, memory = list(program["registers"]), initial_memory(program["memory_seed"])
    counts = {}
    for segment in program["segments"]:
        for _ in range(segment["iterations"]):
            for inst in segment["body"]:
                op, a = inst["op"], regs[inst["a"]]
                b = regs[inst["b"]] if "b" in inst else 0
                counts[op] = counts.get(op, 0) + 1
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
        "operations": counts,
        "useful_work": WORK,
    }


def assembly(program):
    validate(program)
    lines = [
        ".section .text",
        ".option norvc",
        ".global main",
        "main:",
        "  csrwi mcountinhibit, 0",
        "  la s1, data_words",
    ]
    lines += [f"  li a{i}, {v}" for i, v in enumerate(program["registers"])]
    lines += [
        "  csrr s10, mcycle",
        ".global measure_start",
        "measure_start:",
        "  addi s11, zero, 1",
    ]
    for i, segment in enumerate(program["segments"]):
        lines += [
            f"  li s9, {segment['release']}",
            "  add s9, s9, s10",
            f".Lrelease{i}:",
            "  csrr t0, mcycle",
            f"  bltu t0, s9, .Lrelease{i}",
            f"  li t6, {segment['iterations']}",
            f".Lloop{i}:",
        ]
        for j, inst in enumerate(segment["body"]):
            op, a = inst["op"], f"a{inst['a']}"
            b = f"a{inst['b']}" if "b" in inst else None
            d = f"a{inst['dst']}" if "dst" in inst else None
            if op in ("load", "store"):
                lines += [
                    f"  andi t2, {a}, 63",
                    "  slli t2, t2, 2",
                    "  add t2, s1, t2",
                    f"  lw {d}, 0(t2)" if op == "load" else f"  sw {b}, 0(t2)",
                ]
            elif op == "cmovz":
                lines += [
                    f"  bnez {a}, .Lskip{i}_{j}",
                    f"  mv {d}, {b}",
                    f".Lskip{i}_{j}:",
                ]
            else:
                lines.append(f"  {op} {d}, {a}, {b}")
        lines += ["  addi t6, t6, -1", f"  bnez t6, .Lloop{i}"]
    lines += [
        ".global body_complete",
        "body_complete:",
        "  addi s11, zero, 2",
        f"  li s9, {HORIZON + 64}",
        "  add s9, s9, s10",
        ".Lwait:",
        "  csrr t0, mcycle",
        "  bltu t0, s9, .Lwait",
        ".global measure_stop",
        "measure_stop:",
        "  la t0, snapshot",
    ]
    lines += [f"  sw a{i}, {i * 4}(t0)" for i in range(8)]
    lines += [
        "  la a0, state_label",
        "  call puts",
        "  la s2, snapshot",
        "  li s3, 8",
        ".Lprint_regs:",
        "  lw a0, 0(s2)",
        "  call puthex",
        "  li a0, 32",
        "  call putchar",
        "  addi s2, s2, 4",
        "  addi s3, s3, -1",
        "  bnez s3, .Lprint_regs",
        "  la s2, data_words",
        "  li s3, 64",
        ".Lprint_mem:",
        "  lw a0, 0(s2)",
        "  call puthex",
        "  li a0, 32",
        "  call putchar",
        "  addi s2, s2, 4",
        "  addi s3, s3, -1",
        "  bnez s3, .Lprint_mem",
        "  li a0, 10",
        "  call putchar",
        "  call sim_halt",
        ".Lhalt:",
        "  j .Lhalt",
        ".section .rodata",
        'state_label: .asciz "AGCWS_STATE "',
        ".section .data",
        ".balign 4",
        "data_words:",
    ]
    lines += [f"  .word {value}" for value in initial_memory(program["memory_seed"])]
    lines += [".section .bss", ".balign 4", "snapshot: .space 32"]
    return "\n".join(lines) + "\n"


def random_operation(rng, operations=None):
    op = rng.choice(operations or [*BINARY, "load", "store"])
    fields = (
        ("a", "b")
        if op == "store"
        else ("dst", "a")
        if op == "load"
        else ("dst", "a", "b")
    )
    return {"op": op, **{k: rng.randrange(8) for k in fields}}


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
                "iterations": (right - left) * 8 // size,
                "release": releases[len(segments)],
                "body": body,
            }
        )
    return {
        "registers": [
            rng.choice([0, 1, 17, 31, MASK, rng.getrandbits(32)]) for _ in range(8)
        ],
        "memory_seed": rng.getrandbits(32),
        "segments": segments,
    }


def mutate(program, rng):
    candidate = copy.deepcopy(program)
    if rng.random() < 0.2:
        return random_program(rng)
    if rng.random() < 0.3:
        i = rng.randrange(8)
        candidate["registers"][i] ^= 1 << rng.randrange(32)
    elif rng.random() < 0.3:
        rng.choice(candidate["segments"])["release"] = rng.randrange(HORIZON)
    elif rng.random() < 0.3 and len(candidate["segments"]) > 1:
        rng.shuffle(candidate["segments"])
    else:
        body = rng.choice(candidate["segments"])["body"]
        body[rng.randrange(len(body))] = random_operation(rng)
    validate(candidate)
    return candidate


if __name__ == "__main__":
    print(json.dumps(random_program(random.Random(600)), indent=2))
