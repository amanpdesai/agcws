"""Architectural state-change diagnostics, not a redefinition of valid useful work."""

import collections
import gzip
import json
import re
from pathlib import Path

from analysis.solution_audit import read


def changes(program, counts):
    regs = list(program["registers"])
    memory = [(program["memory_seed"] + i * 0x9E3779B9) & 0xFFFFFFFF for i in range(64)]
    unchanged = collections.Counter()
    operations = collections.Counter()
    for segment, count in zip(program["segments"], counts):
        for i in range(count):
            inst = segment["body"][i % len(segment["body"])]
            op = inst["op"]
            a = regs[inst["a"]]
            b = regs[inst["b"]] if "b" in inst else None
            operations[op] += 1
            if op == "store":
                unchanged[op] += memory[a & 63] == b
                memory[a & 63] = b
                continue
            if op == "load":
                value = memory[a & 63]
            elif op == "add":
                value = a + b
            elif op == "mul":
                value = a * b
            elif op == "divu":
                value = a // b if b else 0xFFFFFFFF
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
            elif op == "cmovz":
                value = b if a == 0 else regs[inst["dst"]]
            else:
                raise ValueError(op)
            value &= 0xFFFFFFFF
            unchanged[op] += value == regs[inst["dst"]]
            regs[inst["dst"]] = value
    return {
        "registers": regs,
        "memory": memory,
        "operations": dict(operations),
        "unchanged_operations": dict(unchanged),
        "unchanged_fraction": sum(unchanged.values()) / sum(operations.values()),
    }


def main():
    source = read(Path("results/solution_audit_v1/inspection.json"))
    out = []
    for case in source["cases"]:
        if not case["valid"]:
            continue
        counts = changes(case["program"], case["allocation"])
        base = Path("results/nonflat_temporal_v1/evaluations") / case["cache_id"] / "run"
        expected = read(base / "functional.json.gz")["expected"]
        text = gzip.decompress((base / "ibex_simple_system.log.gz").read_bytes()).decode()
        printed = re.search(r"AGCWS_STATE ([0-9a-fA-F ]+)\n", text)
        actual = [int(v, 16) for v in printed[1].split()] if printed else None
        if actual != counts["registers"] + counts["memory"] or any(
            counts[k] != expected[k] for k in ("registers", "memory", "operations")
        ):
            raise ValueError("actual architectural output or reference differs")
        out.append({k: case[k] for k in ("target", "seed", "arm", "slot", "roles")} | counts)
    result = {
        "cases": out,
        "actual_output_matches": len(out),
        "interpretation": "Unchanged architectural destination is a diagnostic, not proof of useless computation or zero circuit switching. Frozen work remains 4096 semantic operations; no results are rescored.",
    }
    with Path("results/solution_audit_v1/work.json").open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
