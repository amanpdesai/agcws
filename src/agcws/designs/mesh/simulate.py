"""Replay timed packets on four unmodified BaseJump routers, with a scoreboard."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import jsonschema

from agcws.core import config
from agcws.core.build import ensure_binary
from agcws.core.config import ROOT as _REPO_ROOT
from agcws.designs.assets import asset_path
from agcws.evaluation.activity.known_bits import Observation, read_bits

ROOT = _REPO_ROOT
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["packets", "sink_period", "sink_pause"],
    "properties": {
        "sink_period": {"type": "integer", "minimum": 1, "maximum": 256},
        "sink_pause": {"type": "integer", "minimum": 0, "maximum": 255},
        "packets": {"type": "array", "minItems": 64, "maxItems": 4096,
                    "items": {"type": "object", "additionalProperties": False,
                              "required": ["release_cycle", "source", "destination", "payload"],
                              "properties": {
                                  "release_cycle": {"type": "integer", "minimum": 0, "maximum": 8191},
                                  "source": {"type": "integer", "minimum": 0, "maximum": 3},
                                  "destination": {"type": "integer", "minimum": 0, "maximum": 3},
                                  "payload": {"type": "integer", "minimum": 0, "maximum": 4294967295},
                              }}}
    },
}


def packet_program(workload):
    jsonschema.validate(workload, SCHEMA)
    if workload["sink_pause"] >= workload["sink_period"]:
        raise ValueError("sink must accept traffic during every period")
    last = [-1] * 4
    lines = []
    for p in workload["packets"]:
        if p["release_cycle"] < last[p["source"]]:
            raise ValueError("release cycles must be nondecreasing for each source")
        last[p["source"]] = p["release_cycle"]
        lines.append(f"{p['release_cycle']} {p['source']} {p['destination']} {p['payload']:08x}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("positive compile jobs required")
    workload = json.loads(args.workload.read_text())
    program = packet_program(workload)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "program.txt").write_text(program)
    dependency = ROOT / "benchmarks/support/basejump_stl"
    include = dependency / "testing/bsg_noc/bsg_mesh_router/all_to_all/sv.include"
    sources = [Path(line.replace("$BASEJUMP_STL_DIR", str(dependency)))
               for line in include.read_text().splitlines() if line.startswith("$BASEJUMP_STL_DIR")]
    harness = asset_path("mesh", "mesh_temporal.sv")
    sources.append(harness)
    headers = [dependency / "bsg_misc/bsg_defines.sv", dependency / "bsg_noc/bsg_noc_links.svh"]
    version = subprocess.check_output([config.VERILATOR, "--version"], text=True).strip()
    hashes = {("package/mesh/" + p.name if p == harness else str(p.relative_to(ROOT))): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [*sources, *headers]}
    digest = hashlib.sha256(json.dumps({"sources": hashes, "version": version,
                                      "recipe": "mesh2x2-timed-v1"}, sort_keys=True).encode()).hexdigest()
    build = ROOT / "out/.cache" / ("mesh-" + digest)

    def compile_binary(binary):
        command = [str(config.VERILATOR), "--binary", "--timing", "--assert", "--trace",
                   "-Wno-fatal", "--top-module", "mesh_temporal", "-j", str(args.jobs),
                   "--Mdir", str(build), "-o", str(binary),
                   f"-I{dependency / 'bsg_misc'}", f"-I{dependency / 'bsg_noc'}", *map(str, sources)]
        with (out / "compile.log").open("w") as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)

    binary = ensure_binary(build, "simulate", compile_binary)
    with (out / "run.log").open("w") as log:
        subprocess.run([str(binary), f"+PROGRAM={out / 'program.txt'}",
                        f"+SINK_PERIOD={workload['sink_period']}", f"+SINK_PAUSE={workload['sink_pause']}"],
                       cwd=out, check=True, stdout=log, stderr=subprocess.STDOUT)
    match = re.search(r"AGCWS_MESH_DONE sent=(\d+) received=(\d+) cycles=8200", (out / "run.log").read_text())
    if not match or tuple(map(int, match.groups())) != (len(workload["packets"]),) * 2:
        raise RuntimeError("mesh completion/useful-work check failed")
    activity = read_bits(out / "activity.vcd", Observation("mesh_temporal.dut", "mesh_temporal.clk", 8200))
    if activity["clock_edges"] != 8200:
        raise RuntimeError("mesh observation window differs from 8200 clock edges")
    (out / "activity.json").write_text(json.dumps(activity) + "\n")
    (out / "functional.json").write_text(json.dumps({"valid": True,
        "sent": int(match[1]), "received": int(match[2]), "useful_packets": int(match[2]),
        "scoreboard": "all packet IDs, payloads, destinations; no duplicate or unsolicited delivery"}) + "\n")
    (out / "provenance.json").write_text(json.dumps({"sources_sha256": hashes,
        "verilator": version, "simulator_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "build_key": digest, "scope": "mesh_temporal.dut", "fidelity": "activity",
        "observation_cycles": 8200, "reset_cycles": 8,
        "workload_sha256": hashlib.sha256(args.workload.read_bytes()).hexdigest(),
        "program_sha256": hashlib.sha256(program.encode()).hexdigest(),
        "sink_period": workload["sink_period"], "sink_pause": workload["sink_pause"]}, indent=2) + "\n")
    print(json.dumps({"output": str(out), "received": int(match[2]), "clock_edges": 8200}))


if __name__ == "__main__":
    main()
