"""Container replay for v2; retain the unchanged v1 activity-window measurement."""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v1.activity import extract
from experiments.ibex_temporal_v2.compiler import assembly
from experiments.ibex_temporal_v2.program import HORIZON, interpret


def run(source, output, simulator):
    program = json.loads(source.read_text())
    expected = interpret(program)
    assert expected["useful_work"] == 4096
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "program.json").write_text(json.dumps(program, indent=2) + "\n")
    asm, elf = output / "program.S", output / "program.elf"
    asm.write_text(assembly(program))
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
    start = time.monotonic()
    with (output / "compile.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
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
        or [int(x, 16) for x in match[1].split()]
        != expected["registers"] + expected["memory"]
    ):
        raise ValueError("architectural reference mismatch")
    symbols = subprocess.check_output(["riscv64-unknown-elf-nm", str(elf)], text=True)
    pcs = {
        name: int(
            re.search(r"^([0-9a-f]+) \w " + name + r"$", symbols, re.MULTILINE)[1], 16
        )
        for name in ("measure_start", "body_complete", "measure_stop")
    }
    record = {
        "functional_ok": True,
        "expected": expected,
        "marker_pcs": pcs,
        "observation_cycles": HORIZON,
        "wall_clock_s": time.monotonic() - start,
        "inputs": {
            str(p): file_sha256(p)
            for p in (
                asm,
                elf,
                simulator.resolve(),
                Path(__file__),
                Path("experiments/ibex_temporal_v2/compiler.py"),
                Path("experiments/ibex_temporal_v2/program.py"),
            )
        },
    }
    (output / "functional.json").write_text(json.dumps(record, indent=2) + "\n")
    return extract(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--simulator",
        type=Path,
        default=Path(
            "out/toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system"
        ),
    )
    args = parser.parse_args()
    run(args.program, args.out, args.simulator)
