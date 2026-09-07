"""Container-local CPU replay, architectural checking and fixed-window activity."""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v1.program import HORIZON, assembly, interpret


def run(program_path, out, simulator):
    program = json.loads(program_path.read_text())
    expected = interpret(program)
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "program.json").write_text(json.dumps(program, indent=2) + "\n")
    source = out / "program.S"
    source.write_text(assembly(program))
    root = Path("third_party/ibex/examples/sw/simple_system/common").resolve()
    elf = out / "program.elf"
    command = [
        "riscv64-unknown-elf-gcc",
        "-march=rv32im_zicsr",
        "-mabi=ilp32",
        "-nostdlib",
        "-nostartfiles",
        "-ffreestanding",
        "-Wl,--gc-sections",
        "-I",
        str(root),
        "-T",
        str(root / "link.ld"),
        str(root / "crt0.S"),
        str(root / "simple_system_common.c"),
        str(source),
        "-o",
        str(elf),
    ]
    start = time.monotonic()
    with (out / "compile.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    with (out / "simulator.log").open("w") as log:
        subprocess.run(
            [str(simulator.resolve(strict=True)), "--meminit=ram," + str(elf), "-t"],
            cwd=out,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    text = (out / "ibex_simple_system.log").read_text()
    match = re.search(r"AGCWS_STATE ([0-9A-Fa-f ]+)\n", text)
    if not match:
        raise ValueError("missing architectural-state output")
    observed = [int(x, 16) for x in match[1].split()]
    if observed != expected["registers"] + expected["memory"]:
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
                source,
                elf,
                simulator.resolve(),
                Path(__file__),
                Path("experiments/ibex_temporal_v1/program.py"),
            )
        },
    }
    (out / "functional.json").write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "functional_ok": True,
                "marker_pcs": pcs,
                "wall_clock_s": record["wall_clock_s"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--activity", action="store_true")
    parser.add_argument(
        "--simulator",
        type=Path,
        default=Path(
            "out/toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system"
        ),
    )
    args = parser.parse_args()
    run(args.program, args.out, args.simulator)
    if args.activity:
        from experiments.ibex_temporal_v1.activity import extract

        extract(args.out)
