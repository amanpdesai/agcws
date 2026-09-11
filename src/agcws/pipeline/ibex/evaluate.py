"""Replay unchanged instructions with label-based execution diagnostics."""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

from agcws.pipeline.ibex.activity import extract as activity
from agcws.pipeline.ibex.compiler import assembly, phases
from agcws.pipeline.ibex.compiler import unannotated_assembly as original_assembly
from agcws.pipeline.ibex.events import extract as events
from agcws.pipeline.ibex.feedback import extract as feedback
from agcws.pipeline.ibex.program import HORIZON, canonical, interpret
from agcws.provenance import file_sha256


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def run(source, output, simulator, annotated=True):
    program = canonical(json.loads(source.read_text()))
    expected = interpret(program)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    write(output / "program.json", program)
    asm, elf = output / "program.S", output / "program.elf"
    asm.write_text((assembly if annotated else original_assembly)(program))
    runtime = Path("third_party/ibex/examples/sw/simple_system/common").resolve()
    command = [
        "riscv64-unknown-elf-gcc",
        "-march=rv32im_zicsr",
        "-mabi=ilp32",
        "-nostdlib",
        "-nostartfiles",
        "-ffreestanding",
        "-Wl,--gc-sections",
        "-I",
        str(runtime),
        "-T",
        str(runtime / "link.ld"),
        str(runtime / "crt0.S"),
        str(runtime / "simple_system_common.c"),
        str(asm),
        "-o",
        str(elf),
    ]
    started = time.monotonic()
    with (output / "compile.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    subprocess.run(
        [
            "riscv64-unknown-elf-objcopy",
            "-O",
            "binary",
            str(elf),
            str(output / "loadable.bin"),
        ],
        check=True,
    )
    with (output / "simulator.log").open("w") as log:
        subprocess.run(
            [str(simulator.resolve(strict=True)), "--meminit=ram," + str(elf), "-t"],
            cwd=output,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    match = re.search(
        r"AGCWS_STATE ([0-9A-Fa-f ]+)\n",
        (output / "ibex_simple_system.log").read_text(),
    )
    if (
        not match
        or [int(v, 16) for v in match[1].split()] != expected["registers"] + expected["memory"]
    ):
        raise ValueError("architectural reference mismatch")
    nm = subprocess.check_output(["riscv64-unknown-elf-nm", str(elf)], text=True)
    symbols = {
        name: int(address, 16)
        for address, name in re.findall(r"^([0-9a-f]+) \w (\S+)$", nm, re.MULTILINE)
    }
    pcs = {k: symbols[k] for k in ("measure_start", "body_complete", "measure_stop")}
    write(
        output / "functional.json",
        {
            "functional_ok": True,
            "expected": expected,
            "marker_pcs": pcs,
            "observation_cycles": HORIZON,
            "wall_clock_s": time.monotonic() - started,
            "inputs": {
                str(p): file_sha256(p)
                for p in (
                    source.resolve(),
                    asm,
                    elf,
                    output / "loadable.bin",
                    simulator.resolve(),
                    Path(__file__),
                    Path("src/agcws/pipeline/ibex/compiler.py"),
                    Path("src/agcws/pipeline/ibex/events.py"),
                    Path("src/agcws/pipeline/ibex/program.py"),
                    Path("src/agcws/pipeline/ibex/compiler.py"),
                )
            },
        },
    )
    measured = feedback(output)
    write(output / "feedback.json", measured)
    if annotated:
        mapping = phases(symbols, len(program["segments"]))
        write(output / "phase_map.json", mapping)
        with (output / "trace_core_00000000.log").open() as trace:
            next(trace)
            diagnostic = events(trace, measured["begin_tick"], measured["end_tick"], mapping)
        for i, window in enumerate(diagnostic["bins"]):
            if sum(window["retired_by_phase"].values()) != measured["retired_per_bin"][i]:
                raise ValueError("phase/retirement count mismatch")
            if (
                window["divide_zero_divisor"] + window["divide_nonzero_divisor"]
                != measured["retired_classes"][i]["divide"]
            ):
                raise ValueError("divide operand count mismatch")
        write(output / "execution.json", diagnostic)
    return activity(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--original", action="store_true")
    parser.add_argument(
        "--simulator",
        type=Path,
        default=Path(
            "out/toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system"
        ),
    )
    args = parser.parse_args()
    run(args.program, args.out, args.simulator, not args.original)
