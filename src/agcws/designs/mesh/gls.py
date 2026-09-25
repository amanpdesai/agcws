"""Mapped BaseJump replay using the unchanged RTL traffic driver and scoreboard.

Interface: synthesize --out DIR; replay --synthesis DIR --workload JSON
--rtl-waveform VCD --out DIR [--jobs N]. Workloads are elaborated packet lists.
The output is compatible with evaluation.power.windows: clock clk_i, scope
mesh_temporal/dut, expected_edges 8200. No timing back-annotation is claimed.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from agcws.core import config
from agcws.core.build import ensure_binary
from agcws.designs.assets import asset_path
from agcws.designs.mesh.simulate import packet_program
from agcws.evaluation.activity.known_bits import Observation, read_bits
from agcws.evaluation.waveforms.grid import grid

TOP = "agcws_mesh"
CLOCK = "clk_i"
SCOPE = "mesh_temporal/dut"
EDGES = 8200


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def run(command, log, cwd=None):
    # Keep commands and all output, including failed builds and assertions.
    write_json(log.with_suffix(".command.json"), list(map(str, command)))
    with log.open("w") as stream:
        subprocess.run(list(map(str, command)), cwd=cwd, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)


def sources():
    dependency = config.ROOT / "benchmarks/support/basejump_stl"
    include = dependency / "testing/bsg_noc/bsg_mesh_router/all_to_all/sv.include"
    paths = [Path(line.replace("$BASEJUMP_STL_DIR", str(dependency)))
             for line in include.read_text().splitlines()
             if line.startswith("$BASEJUMP_STL_DIR") and "/bsg_test/" not in line]
    headers = [dependency / "bsg_misc/bsg_defines.sv",
               dependency / "bsg_noc/bsg_noc_links.svh", include]
    return paths + [asset_path("mesh", "mesh_temporal.sv")], headers


def yosys_path(path):
    value = str(Path(path).resolve(strict=True))
    if any(c.isspace() or c in ';"\\' for c in value):
        raise ValueError("unsupported Yosys path")
    return value


def synthesize(out):
    rtl, headers = sources()
    liberty = config.LIBERTY.resolve(strict=True)
    plugin = os.environ.get("AGCWS_SLANG_PLUGIN", "")
    prefix = f"plugin -i {yosys_path(plugin)}; " if plugin else ""
    includes = sorted({p.parent for p in headers[:2]})
    script = (prefix + f"read_slang --top {TOP} -D SYNTHESIS "
              + " ".join(f"-I {yosys_path(p)}" for p in includes) + " "
              + " ".join(yosys_path(p) for p in rtl)
              + f"; hierarchy -check -top {TOP}; flatten; proc; opt; memory_map; opt; "
              + f"techmap; opt; dfflibmap -liberty {yosys_path(liberty)}; "
              + f"abc -liberty {yosys_path(liberty)}; clean; "
              + f"read_liberty -lib {yosys_path(liberty)}; check -assert; "
              # Flattened BaseJump array/struct names trigger a Verilator 5.048
              # trace-name hashing bug. Rename internal wires only; ports and
              # mapped-cell instances retain their synthesis identities.
              + f"rename -hide {TOP}/w:*; rename -enumerate {TOP}/w:*; "
              + f"write_verilog -noattr -noexpr {yosys_path(out)}/mapped.v; "
              + f"tee -o {yosys_path(out)}/stat.json stat -json\n")
    (out / "synthesis.ys").write_text(script)
    run([config.YOSYS, "-Q", "-T", "-s", out / "synthesis.ys"], out / "synthesis.log")
    manifest = {"top": TOP, "clock": CLOCK, "scope": SCOPE,
                "expected_edges": EDGES, "reset_cycles": 8,
                "netlist_sha256": sha(out / "mapped.v"), "liberty": str(liberty),
                "liberty_sha256": sha(liberty),
                "sources": {str(p.resolve()): sha(p) for p in rtl + headers},
                "synthesis_script_sha256": sha(out / "synthesis.ys"),
                "yosys_version": subprocess.check_output([str(config.YOSYS), "-V"], text=True).strip()}
    if plugin:
        manifest["plugin_sha256"] = sha(plugin)
    write_json(out / "manifest.json", manifest)
    return manifest


def validate_synthesis(synthesis):
    manifest = json.loads((synthesis / "manifest.json").read_text())
    if (manifest["top"] != TOP or manifest["netlist_sha256"] != sha(synthesis / "mapped.v")
            or manifest["liberty_sha256"] != sha(config.LIBERTY)):
        raise ValueError("mesh netlist/top/Liberty mismatch")
    for name, digest in manifest["sources"].items():
        if sha(name) != digest:
            raise ValueError(f"mesh source changed since synthesis: {name}")
    return manifest


def check_completion(log, expected):
    match = re.search(r"AGCWS_MESH_DONE sent=(\d+) received=(\d+) cycles=8200", log)
    if ("MESH_FUNCTIONAL_MISMATCH" in log or "MESH_INCOMPLETE" in log
            or not match or tuple(map(int, match.groups())) != (expected, expected)):
        raise ValueError("mapped mesh completion/useful-work check failed")
    return {"valid": True, "sent": expected, "received": expected,
            "useful_packets": expected,
            "scoreboard": "all packet IDs, payloads, destinations; no duplicate or unsolicited delivery"}


def validate_rtl(waveform, program, workload, manifest, *, migration_out=None):
    """Require a fresh matched RTL receipt, including source and packet identity."""
    directory = waveform.parent
    expected = len(workload["packets"])
    if (directory / "program.txt").read_text() != program:
        raise ValueError("RTL/GLS packet programs differ")
    functional = json.loads((directory / "functional.json").read_text())
    if (functional.get("valid") is not True or functional.get("sent") != expected
            or functional.get("received") != expected):
        raise ValueError("RTL functional receipt differs")
    provenance = json.loads((directory / "provenance.json").read_text())
    frozen = "third_party/harnesses/mesh_temporal.sv" in provenance["sources_sha256"]
    if frozen:
        from agcws.designs.mesh.frozen import validate
        migration = validate(waveform, workload, manifest, provenance)
        if migration_out is None:
            raise ValueError("frozen mesh replay requires a durable migration receipt")
        write_json(migration_out, migration)
    elif any(provenance.get(key) != workload[key] for key in ("sink_period", "sink_pause")):
        raise ValueError("RTL/GLS sink pacing differs or is unrecorded")
    if (provenance.get("observation_cycles") != EDGES
            or provenance.get("reset_cycles") != 8
            or provenance.get("scope") != "mesh_temporal.dut"):
        raise ValueError("RTL observation contract differs")
    hashes = provenance["sources_sha256"]
    for name, digest in (() if frozen else manifest["sources"].items()):
        path = Path(name)
        if path.name == "sv.include":
            continue
        key = ("package/mesh/" + path.name if path.name == "mesh_temporal.sv"
               else str(path.relative_to(config.ROOT)))
        if hashes.get(key) != digest:
            raise ValueError(f"RTL/synthesis source identity differs: {key}")
    paths = [waveform, directory / "program.txt", directory / "functional.json", directory / "provenance.json"]
    if frozen:
        paths.append(migration_out)
    return {str(p): sha(p) for p in paths}


def replay(synthesis, workload_path, rtl_waveform, out, jobs=2):
    if jobs < 1:
        raise ValueError("positive compile jobs required")
    synthesis = synthesis.resolve(strict=True)
    manifest = validate_synthesis(synthesis)
    workload = json.loads(workload_path.read_text())
    program = packet_program(workload)
    (out / "program.txt").write_text(program)
    rtl_inputs = validate_rtl(rtl_waveform, program, workload, manifest,
                              migration_out=out / "migration.json")
    cells = Path(os.environ["AGCWS_SKY130_CELL_MODELS"]).resolve(strict=True)
    primitives = Path(os.environ["AGCWS_SKY130_PRIMITIVES"]).resolve(strict=True)
    harness = asset_path("mesh", "mesh_temporal.sv")
    inputs = {str(p.resolve()): sha(p) for p in
              (synthesis / "mapped.v", cells, primitives, harness, Path(__file__))}
    version = subprocess.check_output([str(config.VERILATOR), "--version"], text=True).strip()
    key = hashlib.sha256(json.dumps({"inputs": inputs, "version": version,
                                    "recipe": "mesh-mapped-v1"}, sort_keys=True).encode()).hexdigest()
    build = config.ROOT / "out/.cache/mesh-matched-gls" / key

    def compile_binary(binary):
        run([config.VERILATOR, "--binary", "--timing", "--assert", "--trace", "--trace-underscore",
             "-Wno-fatal", "-DAGCWS_MESH_MAPPED", "-DFUNCTIONAL", "-DUNIT_DELAY=",
             "--top-module", "mesh_temporal", "-j", str(jobs), "--Mdir", build,
             "-o", binary, synthesis / "mapped.v", cells, primitives, harness], out / "compile.log")

    binary = ensure_binary(build, "simulate", compile_binary)
    run([binary, f"+PROGRAM={out / 'program.txt'}",
         f"+SINK_PERIOD={workload['sink_period']}", f"+SINK_PAUSE={workload['sink_pause']}"],
        out / "run.log", cwd=out)
    functional = check_completion((out / "run.log").read_text(), len(workload["packets"]))
    write_json(out / "functional.json", functional)
    left = grid(rtl_waveform, CLOCK, EDGES)
    right = grid(out / "activity.vcd", CLOCK, EDGES)
    write_json(out / "grids.json", {"rtl": left, "gls": right, "matched": left == right})
    if left != right:
        raise ValueError("RTL/GLS measurement grids differ")
    activity = read_bits(out / "activity.vcd", Observation("mesh_temporal.dut", "mesh_temporal.clk", EDGES))
    if activity["clock_edges"] != EDGES:
        raise ValueError("mapped mesh observation window differs")
    write_json(out / "activity.json", activity)
    write_json(out / "provenance.json", {
        "fidelity": "zero-delay mapped simulation; no SDF", "top": TOP, "clock": CLOCK,
        "scope": SCOPE, "clock_edges": EDGES, "reset_cycles": 8, "inputs": inputs,
        "rtl_inputs": rtl_inputs, "liberty": manifest["liberty"],
        "sink_period": workload["sink_period"], "sink_pause": workload["sink_pause"],
        "synthesis_manifest_sha256": sha(synthesis / "manifest.json"),
        "liberty_sha256": manifest["liberty_sha256"], "build_key": key, "verilator": version,
        "simulator_sha256": sha(binary), "program_sha256": sha(out / "program.txt"),
        "workload_sha256": sha(workload_path), "waveform_sha256": sha(out / "activity.vcd"),
        "rtl_waveform_sha256": sha(rtl_waveform), "matched_grid": right,
        "packets_checked": functional["received"]})
    return functional


def replay_trial(rtl: Path, synthesis: Path, out: Path) -> dict:
    """Shared dispatcher adapter; require the original attempt's strict receipt."""
    rtl, synthesis, out = rtl.resolve(strict=True), synthesis.resolve(strict=True), out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    try:
        replay(synthesis, rtl / "workload.json", rtl / "activity.vcd", out)
    except Exception as error:
        write_json(out / "failure.json", {"stage": "replay", "error": str(error),
                                          "type": type(error).__name__})
        raise
    return {"waveform": out / "activity.vcd", "rtl_waveform": rtl / "activity.vcd",
            "clock": CLOCK, "rtl_clock": CLOCK, "scope": SCOPE, "clock_edges": EDGES,
            "bounds": None, "expected_period_s": 1e-8}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["synthesize", "replay"])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--synthesis", type=Path)
    parser.add_argument("--workload", type=Path)
    parser.add_argument("--rtl-waveform", type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("positive compile jobs required")
    if args.stage == "replay" and not all((args.synthesis, args.workload, args.rtl_waveform)):
        parser.error("replay requires --synthesis, --workload and --rtl-waveform")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    try:
        if args.stage == "synthesize":
            synthesize(out)
        else:
            replay(args.synthesis, args.workload.resolve(), args.rtl_waveform.resolve(), out, args.jobs)
    except Exception as error:
        write_json(out / "failure.json", {"stage": args.stage, "error": str(error),
                                          "type": type(error).__name__})
        raise
    print(f"MESH_MATCHED_GLS_{args.stage.upper()}_DONE {out}", flush=True)


if __name__ == "__main__":
    main()
