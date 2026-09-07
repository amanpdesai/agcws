"""Compile weighted programs, including final partial loop iterations."""

from experiments.ibex_temporal_v1 import program as v1
from experiments.ibex_temporal_v2.program import HORIZON, allocation


def instruction(inst, label):
    op, a = inst["op"], f"a{inst['a']}"
    b = f"a{inst['b']}" if "b" in inst else None
    dst = f"a{inst['dst']}" if "dst" in inst else None
    if op in ("load", "store"):
        return [
            f"  andi t2, {a}, 63",
            "  slli t2, t2, 2",
            "  add t2, s1, t2",
            f"  lw {dst}, 0(t2)" if op == "load" else f"  sw {b}, 0(t2)",
        ]
    if op == "cmovz":
        return [f"  bnez {a}, {label}", f"  mv {dst}, {b}", f"{label}:"]
    return [f"  {op} {dst}, {a}, {b}"]


def assembly(program):
    counts = allocation(program)
    if all(
        count % len(s["body"]) == 0 for s, count in zip(program["segments"], counts)
    ):
        lowered = {
            **program,
            "segments": [
                {
                    "iterations": count // len(s["body"]),
                    "release": s["release"],
                    "body": s["body"],
                }
                for s, count in zip(program["segments"], counts)
            ],
        }
        return v1.assembly(lowered)
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
    for i, (segment, count) in enumerate(zip(program["segments"], counts)):
        full, tail = divmod(count, len(segment["body"]))
        lines += [
            f"  li s9, {segment['release']}",
            "  add s9, s9, s10",
            f".Lrelease{i}:",
            "  csrr t0, mcycle",
            f"  bltu t0, s9, .Lrelease{i}",
        ]
        if full:
            lines += [f"  li t6, {full}", f".Lloop{i}:"]
            for j, inst in enumerate(segment["body"]):
                lines += instruction(inst, f".Lskip{i}_{j}")
            lines += ["  addi t6, t6, -1", f"  bnez t6, .Lloop{i}"]
        for j, inst in enumerate(segment["body"][:tail]):
            lines += instruction(inst, f".Ltail_skip{i}_{j}")
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
    lines += [f"  .word {v}" for v in v1.initial_memory(program["memory_seed"])]
    lines += [".section .bss", ".balign 4", "snapshot: .space 32"]
    return "\n".join(lines) + "\n"
