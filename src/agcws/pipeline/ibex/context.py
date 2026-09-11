"""Fixed hardware semantics and compact measured history; no transport code."""

import json

from agcws.pipeline.ibex.program import SCHEMA

PROMPT = 'Construct bounded CPU programs to match the requested eight-bin activity profile.\nReturn strict JSON {"hypothesis": "short testable prediction", "candidates": [programs]}.\nUse the complete schema. Return the requested number of candidates. Use feedback to\nchange complete programs, including operands, instruction mix, segment placement and\ndependencies. Do not merely change a few scalar fields. Do not modify hardware or tools.\nUse positive segment weights, not iteration counts. The common allocator assigns\nexactly 4096 semantic operations. All work must finish inside 200000 cycles.\nMissing and invalid candidates consume budget. Do not repeat failed strategies.\n'

SEMANTICS = "Ibex is an in-order RV32IM CPU, fast multiplier, instruction cache off.\nregisters initializes eight mutable 32-bit registers, addressed by indices 0..7.\nadd/mul wrap modulo 2^32; shifts mask the amount to five bits; divu is unsigned\nand returns 0xffffffff for divisor zero. Division with nonzero divisor stalls\nthe pipeline substantially longer than zero division or ordinary ALU operations.\ncmovz copies register b to dst only if register a is zero; it lowers to a real\nconditional branch. Memory holds 64 words initialized by (memory_seed+i*0x9e3779b9)\nmodulo 2^32. load/store index memory by the low six bits of register a; stores\nwrite register b. Registers and memory persist across iterations and segments.\nEach segment waits until release cycles after measurement start, then executes\nits allocated operation count by cycling its body: whole iterations followed\nby a final prefix. Positive integer weights in [1,4096] specify proportions,\nnot operation counts. Integer largest-remainder allocation (ties by index)\nassigns 4096 total operations; any zero allocation receives one from the largest\nallocation (ties by index). The evaluator reports the actual allocation. Releases already passed do not\nrewind time. Waiting is an active CSR/branch loop, NOT sleep or zero activity.\nThe controller measures core-net bit changes, excluding clocks and CSR counters;\nlower instruction retirement rate need not imply higher or lower switching.\nAll register and memory results are independently reference-checked.\n"


def build_payload(adapter, goal, history, n, system_prompt):
    valid = sorted((t for t in history if t["valid"]), key=lambda t: t["loss"])[:4]
    selected = {t["slot"]: t for t in [*valid, *history[-4:]]}
    compact = [
        {
            k: t[k]
            for k in (
                "slot",
                "program",
                "valid",
                "reason",
                "loss",
                "rates",
                "residual",
                "allocation",
            )
        }
        for t in selected.values()
    ]
    return json.dumps(
        {
            "system_prompt": system_prompt,
            "semantics": SEMANTICS,
            "schema": SCHEMA,
            "goal": goal,
            "history": compact,
            "batch_size": n,
        },
        sort_keys=True,
    )
