#!/usr/bin/env python3
"""Compile an Ibex DSL workload into an ELF for the upstream simple system."""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from agcws.adapters.ibex import IbexAdapter

SIMPLE_SYSTEM_RAM_BASE = 0x100000


def assembly_for(workload: dict) -> str:
    """Return deterministic RV32IM assembly for a validated workload."""
    adapter = IbexAdapter()
    schema = adapter.validate_schema(workload)
    if not schema.valid:
        raise ValueError(f"schema-invalid workload: {schema.reason}")
    protocol = adapter.validate_protocol(workload)
    if not protocol.valid:
        raise ValueError(f"protocol-invalid workload: {protocol.reason}")

    lines = [
        '.section .text',
        '.global main',
        '.type main, @function',
        'main:',
    ]
    for index, instruction in enumerate(workload["program"]):
        op = instruction["op"]
        if op == "nop":
            lines.append("  nop")
        elif op == "addi":
            lines.append(f"  addi t0, t0, {int(instruction.get('immediate', 1))}")
        elif op in {"add", "and", "or", "xor"}:
            lines.append(f"  {op} t0, t0, t1")
        elif op in {"lw", "sw"}:
            address = SIMPLE_SYSTEM_RAM_BASE + int(instruction["address"])
            lines.extend([f"  li t2, {address}", f"  {op} t1, 0(t2)"])
        elif op in {"beq", "bne"}:
            lines.append(f"  {op} t0, t1, .L{instruction['target'] // 4}")
        elif op == "ecall":
            # The simple-system runtime reserves 0x20008 for deterministic halt.
            lines.extend(["  li t2, 0x20008", "  li t1, 1", "  sw t1, 0(t2)"])
        else:  # guarded by validate_protocol; retained for defensive callers
            raise ValueError(f"unsupported instruction: {op}")
        lines.append(f".L{index}:")
    lines.extend(["  ret", ".size main, .-main", ""])
    return "\n".join(lines)


def compile_workload(workload_path: Path, output: Path, *, gcc: str, objcopy: str) -> None:
    workload = json.loads(workload_path.read_text())
    assembly = assembly_for(workload)
    repo_root = Path(__file__).resolve().parents[1]
    ibex_root = repo_root / "third_party" / "ibex"
    crt = ibex_root / "examples" / "sw" / "simple_system" / "common" / "crt0.S"
    runtime = ibex_root / "examples" / "sw" / "simple_system" / "common" / "simple_system_common.c"
    linker = ibex_root / "examples" / "sw" / "simple_system" / "common" / "link.ld"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="agcws-ibex-") as temp_dir:
        source = Path(temp_dir) / "workload.S"
        source.write_text(assembly)
        command = [
            gcc, "-march=rv32im_zicsr", "-mabi=ilp32", "-nostdlib", "-nostartfiles",
            "-ffreestanding", "-Wl,--gc-sections", "-I", str(ibex_root / "examples" / "sw" / "simple_system" / "common"),
            "-T", str(linker), str(crt), str(runtime), str(source), "-o", str(output),
        ]
        subprocess.run(command, check=True)
        # Keep a binary alongside the ELF for tools that cannot consume ELF.
        subprocess.run([objcopy, "-O", "binary", str(output), str(output.with_suffix(".bin"))], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--gcc", default="riscv64-unknown-elf-gcc")
    parser.add_argument("--objcopy", default="riscv64-unknown-elf-objcopy")
    args = parser.parse_args()
    compile_workload(args.workload, args.output, gcc=args.gcc, objcopy=args.objcopy)


if __name__ == "__main__":
    main()
