"""Build and replay reference-checked timed GEMM jobs on a prepared RTL closure."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from agcws.core import config
from agcws.core.build import ensure_binary
from agcws.core.config import ROOT as _REPO_ROOT
from agcws.designs.assets import asset_path
from agcws.designs.redmule.adapter import RedmuleTemporalAdapter, stimulus_headers
from agcws.evaluation.activity.known_bits import Observation, read_bits

ROOT = _REPO_ROOT


def source_hashes(source_list):
    """Fail on unknown directives rather than caching an incomplete RTL closure."""
    package = Path(__file__).resolve().parent
    files = {source_list.resolve(), package / "prepare.py", Path(__file__).resolve(),
             ROOT / "benchmarks/redmule/target/sim/src/redmule_tb.sv",
             ROOT / "benchmarks/redmule/target/sim/src/redmule_tb_wrap.sv"}
    for raw in source_list.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("+define+"):
            continue
        if line.startswith("+incdir+"):
            directory = Path(line.removeprefix("+incdir+"))
            if not directory.is_dir():
                raise ValueError(f"missing source include directory: {directory}")
            files.update(p for p in directory.rglob("*") if p.suffix in (".v", ".sv", ".vh", ".svh"))
        else:
            path = Path(line)
            if not path.is_absolute() or not path.is_file():
                raise ValueError(f"unresolved source-list entry: {line}")
            files.add(path)
    def key(path):
        path = path.resolve()
        if path.is_relative_to(package):
            return "package/redmule/" + str(path.relative_to(package))
        return str(path.relative_to(ROOT))

    return {key(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(files)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload", type=Path)
    parser.add_argument("--source-list", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--observation-cycles", type=int, choices=(65536, 262144), default=65536)
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("positive compile jobs required")
    workload = json.loads(args.workload.read_text())
    cycles = args.observation_cycles
    headers = stimulus_headers(workload, observation_cycles=cycles)
    releases = RedmuleTemporalAdapter(cycles).elaborate(workload)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    inc = out / "inc"
    inc.mkdir(exist_ok=False)
    for name, content in headers.items():
        (inc / name).write_text(content)
    version = subprocess.check_output([config.VERILATOR, "--version"], text=True).strip()
    hashes = source_hashes(args.source_list)
    digest = hashlib.sha256(json.dumps({"sources": hashes, "verilator": version,
                                      "recipe": "redmule4x4-explicit-window-v2"}, sort_keys=True).encode()).hexdigest()
    build = ROOT / "out/.cache" / ("redmule-" + digest)

    def compile_binary(binary):
        derived = build / "harness"
        # Each failed build gets a fresh derivation; no stale partial source output is reused.
        if derived.exists():
            derived = build / f"harness-{len(list(build.glob('harness*')))}"
        subprocess.run([sys.executable, "-m", "agcws.designs.redmule.prepare",
                        "--source-list", str(args.source_list.resolve()), "--out", str(derived)], check=True)
        command = [str(config.VERILATOR), "--binary", "--trace-fst", "--timing", "--assert",
                   "-Wno-fatal", "-Wno-ENUMVALUE", "--top-module", "redmule_tb_wrap",
                   "-GHeight=4", "-GWidth=4", "-j", str(args.jobs), "--Mdir", str(build),
                   "-o", str(binary), "-f", str(derived / "sources.vlt")]
        with (out / "compile.log").open("w") as log:
            subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)

    binary = ensure_binary(build, "simulate", compile_binary)
    software = out / "build"
    command = ["make", "-C", str(ROOT / "benchmarks/redmule"), "sw-build", "REDMULE_COMPLEX=0",
               "target=verilator", "Gcc=", "XLEN=64", "CC=riscv64-unknown-elf-gcc", "LD=riscv64-unknown-elf-gcc",
               "CC_OPTS=-march=rv32imc_zicsr -mabi=ilp32 -O2 -g -ffunction-sections -fdata-sections "
               f"-isystem /usr/lib/picolibc/riscv64-unknown-elf/include -I{inc}",
               "LD_OPTS=-march=rv32imc_zicsr -mabi=ilp32 -nostartfiles -nostdlib -Wl,--gc-sections",
               f"INC_DIR={inc}", f"BUILD_DIR={software}",
               f"TEST_SRCS={asset_path('redmule', 'redmule_temporal.c')}"]
    with (out / "software.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    with (out / "run.log").open("w") as log:
        subprocess.run([str(binary), f"+STIM_INSTR={software / 'stim_instr.txt'}",
                        f"+STIM_DATA={software / 'stim_data.txt'}", f"+OBSERVATION_CYCLES={cycles}"],
                       cwd=out, stdout=log, stderr=subprocess.STDOUT, check=True)
    log = (out / "run.log").read_text()
    jobs = [tuple(map(int, values)) for values in re.findall(
        r"AGCWS_REDMULE_JOB job=(\d+) cycle=(\d+) errors=(\d+)", log)]
    if (len(jobs) != len(releases) or [j[0] for j in jobs] != list(range(len(releases)))
            or any(j[2] or not release <= j[1] < cycles for release, j in zip(releases, jobs, strict=True))
            or "[TB] - errors=00000000" not in log or f"AGCWS_REDMULE_WINDOW_DONE cycles={cycles}" not in log):
        raise RuntimeError("RedMulE completion/reference record differs from requested jobs")
    useful_work = len(jobs) * workload["size"]**3
    functional = {"valid": useful_work >= RedmuleTemporalAdapter.useful_work_floor,
                  "completed_jobs": len(jobs), "useful_work": useful_work,
                  "checked_outputs": len(jobs)*workload["size"]**2, "job_completions": jobs}
    (out / "functional.json").write_text(json.dumps(functional) + "\n")
    if not functional["valid"]:
        raise RuntimeError("REDMULE_USEFUL_WORK below 1024 completed multiply-accumulates")
    subprocess.run(["fst2vcd", "-o", str(out / "activity.vcd"), str(out / "activity.fst")], check=True)
    scope = "redmule_tb_wrap.i_redmule_tb.i_redmule_wrap"
    activity = read_bits(out / "activity.vcd", Observation(scope, "redmule_tb_wrap.clk", cycles))
    if activity["clock_edges"] != cycles:
        raise RuntimeError(f"RedMulE observation window differs from {cycles} cycles")
    (out / "activity.json").write_text(json.dumps(activity) + "\n")
    (out / "provenance.json").write_text(json.dumps({"sources_sha256": hashes, "verilator": version,
        "build_key": digest, "simulator_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "stimulus_headers_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in headers.items()},
        "scope": scope, "clock": "redmule_tb_wrap.clk", "fidelity": "activity",
        "observation_cycles": cycles, "functional": functional}, indent=2) + "\n")
    print(json.dumps({"output": str(out), "completed_jobs": len(jobs), "useful_work": useful_work}))


if __name__ == "__main__":
    main()
