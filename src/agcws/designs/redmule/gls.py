"""Matched 4x4 RedMulE GLS preparation; no shared replay aliases are registered.

Keep the timed CPU/reference/memory harness and replace only its accelerator.
The generated synthesis top has explicit scalar ports: no inferred interface
flattening names, behavioral memory black boxes, or default 8x8 configuration.
"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from agcws.designs.redmule.adapter import RedmuleTemporalAdapter, stimulus_headers
from agcws.designs.redmule.bus_trace import triggers
from agcws.designs.redmule.compat import functional_primitives
from agcws.designs.redmule.prepare import timed_testbench, timed_wrapper

TOP = "agcws_redmule_4x4"
SCOPE = "redmule_tb_wrap.i_redmule_tb.i_redmule_wrap"
CLOCK = "redmule_tb_wrap.clk"
PARAMETERS = dict(Height=4, Width=4, DataW=128, NumPipeRegs=1,
                  MisalignedAccessSupport=1, EnableReordering=0, LatchBuffers=0)
# Direction is relative to the accelerator. Include unused ECC ports as well.
TCDM = {
    "req": ("output", 1), "gnt": ("input", 1), "add": ("output", 32),
    "wen": ("output", 1), "data": ("output", 160), "be": ("output", 20),
    "r_ready": ("output", 1), "user": ("output", 1), "id": ("output", 8),
    "r_data": ("input", 160), "r_valid": ("input", 1), "r_user": ("input", 1),
    "r_id": ("input", 8), "r_opc": ("input", 1), "ecc": ("output", 1),
    "r_ecc": ("input", 1), "ereq": ("output", 1), "egnt": ("input", 1),
    "r_evalid": ("input", 1), "r_eready": ("output", 1),
}
TARGET = {
    "req": ("input", 1), "gnt": ("output", 1), "add": ("input", 32),
    "wen": ("input", 1), "be": ("input", 4), "data": ("input", 32),
    "id": ("input", 4), "r_data": ("output", 32), "r_valid": ("output", 1),
    "r_id": ("output", 4),
}
SCALARS = {"clk_i": ("input", 1), "rst_ni": ("input", 1),
           "test_mode_i": ("input", 1), "busy_o": ("output", 1),
           "evt_o": ("output", 1), "sync_o": ("output", 1), "sync_i": ("input", 1)}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def ports():
    return {**SCALARS, **{f"tcdm_{k}": v for k, v in TCDM.items()},
            **{f"target_{k}": v for k, v in TARGET.items()}}


def synthesis_top():
    declarations = [f"  {direction} wire " + (f"[{width-1}:0] " if width > 1 else "") + name
                    for name, (direction, width) in ports().items()]
    assignments = []
    for interface, fields in (("tcdm", TCDM), ("target", TARGET)):
        for field, (direction, _) in fields.items():
            inner, outer = f"{interface}.{field}", f"{interface}_{field}"
            lhs, rhs = (outer, inner) if direction == "output" else (inner, outer)
            assignments.append(f"  assign {lhs} = {rhs};")
    return (f"module {TOP} (\n" + ",\n".join(declarations) + "\n);\n"
            "  import hci_package::*;\n"
            "  localparam hci_size_parameter_t HciSize = '{DW:160, AW:32, BW:8, UW:1, IW:8, EW:1, EHW:1};\n"
            "  hci_core_intf #(.DW(160), .UW(1)) tcdm (.clk(clk_i));\n"
            "  hwpe_ctrl_intf_periph #(.ID_WIDTH(4)) target (.clk(clk_i));\n"
            + "\n".join(assignments) + "\n  redmule_mm_wrap #(\n"
            + ",\n".join(f"    .{k}({v})" for k, v in PARAMETERS.items())
            + ",\n    .HCI_SIZE_tcdm(HciSize)\n  ) dut (\n"
            + ",\n".join(f"    .{k}({k})" for k in SCALARS)
            + ",\n    .tcdm(tcdm), .target(target)\n  );\nendmodule\n")


def gate_testbench(original):
    text = timed_testbench(original)
    start = text.index("  redmule_mm_wrap #(\n")
    end = text.index("\n  tb_dummy_memory", start)
    connections = dict(clk_i="clk_i", rst_ni="rst_ni", test_mode_i="test_mode",
                       busy_o="redmule_busy", evt_o="redmule_evt", sync_o="", sync_i="1'b0")
    connections.update({f"tcdm_{key}": f"redmule_tcdm.{key}" for key in TCDM})
    connections.update({f"target_{key}": f"periph.{key}" for key in TARGET})
    replacement = (f"  {TOP} i_redmule_wrap (\n" + ",\n".join(
        f"    .{key}({value})" for key, value in connections.items()) + "\n  );\n")
    return text[:start] + replacement + text[end:]


def resolve_sources(source_list, dependency_root):
    """Translate only the documented container mount, retaining order/defines."""
    lines, files = [], {source_list.resolve()}
    for raw in source_list.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("+define+"):
            if not re.fullmatch(r"\+define\+[A-Za-z_][A-Za-z_0-9]*(=\w+)?", line):
                raise ValueError(f"unsupported define: {line}")
            lines.append(line)
            continue
        prefix = "+incdir+" if line.startswith("+incdir+") else ""
        value = line.removeprefix(prefix)
        if value.startswith("/workspace/.dependencies/"):
            path = dependency_root / value.removeprefix("/workspace/.dependencies/")
        else:
            path = Path(value)
        if not path.is_absolute():
            raise ValueError(f"unresolved source entry: {line}")
        path = path.resolve(strict=True)
        safe_path(path)
        if prefix:
            if not path.is_dir():
                raise ValueError(f"not an include directory: {path}")
            files.update(p for p in path.rglob("*") if p.suffix in (".sv", ".svh", ".v", ".vh"))
        else:
            if not path.is_file():
                raise ValueError(f"not a source file: {path}")
            files.add(path)
        lines.append(prefix + str(path))
    return list(dict.fromkeys(lines)), files


def safe_path(path):
    # Paths are also emitted into Yosys scripts and simulator response files.
    if not re.fullmatch(r"[A-Za-z0-9_./+:-]+", str(path)):
        raise ValueError(f"unsupported tool path: {path}")
    return str(path)


def prepare(source_list, dependency_root, out, liberty, plugin):
    lines, files = resolve_sources(source_list, dependency_root)
    benches = {}
    for name in ("redmule_tb.sv", "redmule_tb_wrap.sv"):
        matches = [Path(line) for line in lines if line.endswith("/" + name)]
        if len(matches) != 1:
            raise ValueError(f"exactly one {name} required")
        benches[name] = matches[0]
    out.mkdir(parents=True, exist_ok=False)
    for path in (out, liberty, plugin):
        safe_path(path)
    (out / "synthesis_top.sv").write_text(synthesis_top())
    (out / "redmule_tb.sv").write_text(gate_testbench(benches["redmule_tb.sv"].read_text()))
    (out / "redmule_tb_wrap.sv").write_text(timed_wrapper(benches["redmule_tb_wrap.sv"].read_text()))
    replay = [str(out / Path(line).name) if line in map(str, benches.values()) else line for line in lines]
    (out / "replay.vlt").write_text("\n".join(replay) + "\n")
    latch_map = Path(__file__).parent / "assets/sky130_latches.v"
    # Elaboration prunes CPU and test memory; do not feed testbench modules to synthesis.
    design = [line for line in lines if not (line in map(str, benches.values())
              or "/target/sim/" in line or "/common_verification-" in line
              # Unused dependency tops: duplicate mem_to_banks definition and
              # generic string-typed SIMD mask respectively. Neither is in the
              # accelerator hierarchy; hierarchy -check rejects missing users.
              or Path(line).name in ("axi_to_mem.sv", "fpnew_top.sv"))]
    frontend = []
    for line in design:
        if line.startswith("+define+"):
            frontend.extend(["-D", line.removeprefix("+define+")])
        elif line.startswith("+incdir+"):
            frontend.extend(["-I", line.removeprefix("+incdir+")])
        else:
            frontend.append(line)
    frontend.append(str(out / "synthesis_top.sv"))
    script = (f"plugin -i {plugin}\nread_slang --top {TOP} --relax-enum-conversions "
              f"--diag-json {out}/diagnostics.json -D SYNTHESIS " + " ".join(frontend)
              + f"\nhierarchy -check -top {TOP}\nflatten\nproc\nopt\nmemory_map\nopt\n"
              + f"techmap\nopt\ndfflibmap -liberty {liberty}\n"
              + f"techmap -map {latch_map}\nabc -liberty {liberty}\nclean\n"
              # Preserve public ports; normalize internal escaped hierarchical
              # names that trigger Verilator 5.048's reverse-hash-map failure.
              + "rename -hide\nrename -enumerate\n"
              + f"write_verilog -noattr -noexpr {out}/mapped.v\nwrite_json {out}/mapped.json\n")
    (out / "synthesis.ys").write_text(script)
    files.update(Path(__file__).parent / name for name in (
        "gls.py", "prepare.py", "adapter.py", "bus_trace.py", "compat.py"))
    files.add(Path(__file__).parent / "assets/redmule_temporal.c")
    files.add(latch_map)
    generated = {name: sha(out / name) for name in ("synthesis_top.sv", "redmule_tb.sv",
                 "redmule_tb_wrap.sv", "replay.vlt", "synthesis.ys")}
    manifest = dict(schema=1, status="prepared-not-simulated", top=TOP, parameters=PARAMETERS,
                    scope=SCOPE, clock=CLOCK, sources={str(p): sha(p) for p in sorted(files)},
                    generated=generated, liberty=str(liberty), liberty_sha256=sha(liberty),
                    synthesis_excluded_sources=[line for line in lines if line not in design],
                    plugin=str(plugin), plugin_sha256=sha(plugin),
                    dependency_root=str(dependency_root),
                    memory_policy="accelerator storage mapped to logic; unchanged external tb_dummy_memory",
                    timing="zero-delay functional GLS; no SDF or power claim")
    write_json(out / "preparation.json", manifest)
    return manifest


def validate_completion(log, workload, cycles):
    releases = RedmuleTemporalAdapter(cycles).elaborate(workload)
    jobs = [tuple(map(int, values)) for values in re.findall(
        r"AGCWS_REDMULE_JOB job=(\d+) cycle=(\d+) errors=(\d+)", log)]
    if (len(jobs) != len(releases) or [j[0] for j in jobs] != list(range(len(releases)))
            or any(j[2] or not release <= j[1] < cycles for release, j in zip(releases, jobs))
            or log.count(f"AGCWS_REDMULE_WINDOW_DONE cycles={cycles}") != 1
            or "[TB] - errors=00000000" not in log
            or re.search(r"REDMULE_INCOMPLETE|REDMULE_USEFUL_WORK|\[TB\] - Fail|%Error|FATAL", log)):
        raise ValueError("completion/reference/window record differs from requested GEMM jobs")
    work = len(jobs) * workload["size"]**3
    if work < RedmuleTemporalAdapter.useful_work_floor:
        raise ValueError("useful work below 1024 MACs")
    return dict(valid=True, completed_jobs=len(jobs), useful_work=work,
                checked_outputs=len(jobs)*workload["size"]**2, job_completions=jobs)


def validate_mapped(netlist_json, cell_names):
    modules = json.loads(netlist_json.read_text())["modules"]
    if TOP not in modules:
        raise ValueError("mapped top missing")
    top = modules[TOP]
    actual = {name: (port["direction"], len(port["bits"])) for name, port in top["ports"].items()}
    if actual != ports():
        raise ValueError("mapped port contract differs")
    cells = top.get("cells", {})
    if not cells or top.get("memories"):
        raise ValueError("empty mapped design or residual behavioral memory")
    unknown = {cell["type"] for cell in cells.values()} - set(cell_names)
    if unknown:
        raise ValueError(f"unmapped or unsupported cells: {sorted(unknown)}")
    return len(cells)


def verify_preparation(out):
    manifest = json.loads((out / "preparation.json").read_text())
    if manifest["top"] != TOP or manifest["parameters"] != PARAMETERS:
        raise ValueError("synthesis configuration differs")
    inputs = {**manifest["sources"], **{str(out / k): v for k, v in manifest["generated"].items()},
              manifest["liberty"]: manifest["liberty_sha256"], manifest["plugin"]: manifest["plugin_sha256"]}
    for path, digest in inputs.items():
        if sha(path) != digest:
            raise ValueError(f"preparation input hash differs: {path}")
    return manifest


def run(command, log, cwd=None):
    with log.open("w") as stream:
        subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT, check=True)


def synthesize(out, yosys):
    manifest = verify_preparation(out)
    run([yosys, "-Q", "-T", "-s", str(out / "synthesis.ys")], out / "synthesis.log")
    names = re.findall(r"\bcell\s*\(\s*\"?([\w]+)\"?\s*\)", Path(manifest["liberty"]).read_text())
    count = validate_mapped(out / "mapped.json", names)
    write_json(out / "synthesis_manifest.json", dict(
        preparation_sha256=sha(out / "preparation.json"), netlist_sha256=sha(out / "mapped.v"),
        inventory_sha256=sha(out / "mapped.json"), mapped_cells=count,
        yosys_version=subprocess.check_output([yosys, "-V"], text=True).strip()))


def waveform_bounds(path, cycles):
    """Check actual timestamps as well as edge count; all bounds are picoseconds."""
    audit = triggers(path)
    if audit["clock_edges"] != cycles:
        raise ValueError("waveform edge count differs")
    clock_code, scope, timescale = None, [], ""
    edges, now, last_value, last_timestamp = [], 0, None, None
    with path.open() as stream:
        header = []
        for line in stream:
            header.append(line)
            words = line.split()
            if words[:1] == ["$scope"]:
                scope.append(words[2])
            elif words[:1] == ["$upscope"]:
                scope.pop()
            elif (words[:1] == ["$var"] and scope == ["redmule_tb_wrap"]
                  and words[4] == "clk"):
                clock_code = words[3]
            elif words[:1] == ["$enddefinitions"]:
                break
        match = re.search(r"\$timescale\s+(\d+)\s*(\w+)\s+\$end", "".join(header))
        if match:
            timescale = "".join(match.groups())
        if timescale != "1ps" or clock_code is None:
            raise ValueError("expected 1ps waveform and exact clock path")
        for line in stream:
            if line.startswith("#"):
                now = int(line[1:])
                last_timestamp = now
            elif line[:1] in "01xz" and line[1:].strip() == clock_code:
                value = line[0]
                if value == "1" and last_value == "0":
                    edges.append(now)
                last_value = value
    if edges != list(range(500, cycles * 1000, 1000)):
        raise ValueError("waveform clock period/phase differs")
    # Trace converters may omit the final timestamp with no signal changes.
    if last_timestamp not in (edges[-1], edges[-1] + 1):
        raise ValueError("waveform extends beyond the fixed window")
    return dict(clock=CLOCK, scope=SCOPE, timescale="1ps", clock_period_ps=1000,
                clock_edges=cycles, first_rising_edge_ps=edges[0], last_rising_edge_ps=edges[-1],
                observation_start_ps=0, harness_finish_ps=edges[-1]+1,
                waveform_last_timestamp_ps=last_timestamp, includes_reset_and_boot=True,
                accepted_trigger_edges=audit["accepted_trigger_edges"])


def replay(prepared, reference, out, cells, primitives, verilator, fst2vcd, jobs,
           frozen_receipt=None):
    """Replay the exact software images from an independently checked RTL attempt."""
    manifest = verify_preparation(prepared)
    synthesis = json.loads((prepared / "synthesis_manifest.json").read_text())
    for name, field in (("preparation.json", "preparation_sha256"), ("mapped.v", "netlist_sha256"),
                        ("mapped.json", "inventory_sha256")):
        if sha(prepared / name) != synthesis[field]:
            raise ValueError(f"synthesis artifact differs: {name}")
    workload = json.loads((reference / "program.json").read_text())
    provenance = json.loads((reference / "provenance.json").read_text())
    cycles = provenance["observation_cycles"]
    if provenance["scope"] != SCOPE or provenance["clock"] != CLOCK:
        raise ValueError("reference measurement identity differs")
    expected_headers = stimulus_headers(workload, observation_cycles=cycles)
    for name, content in expected_headers.items():
        digest = hashlib.sha256(content.encode()).hexdigest()
        if (sha(reference / "inc" / name) != digest
                or provenance["stimulus_headers_sha256"][name] != digest):
            raise ValueError(f"reference stimulus differs: {name}")
    # Require the RTL source closure to be the same bytes, including harness sources.
    # Do not equate paths or bless a moved runtime solely because it still compiles.
    rtl_hashes = {k: v for k, v in provenance["sources_sha256"].items()
                  if Path(k).suffix in (".sv", ".svh", ".v", ".vh")}
    if not rtl_hashes:
        raise ValueError("empty RTL source closure")
    for name, digest in rtl_hashes.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("unsafe RTL source path")
        if path.parts[0] == ".dependencies":
            source = Path(manifest["dependency_root"]).joinpath(*path.parts[1:])
        elif name.startswith(("third_party/redmule/", "benchmarks/redmule/")):
            # The RTL driver also hashes the pinned upstream harness templates.
            relative = name.removeprefix("third_party/redmule/").removeprefix("benchmarks/redmule/")
            source = Path(manifest["dependency_root"]) / "rtl" / relative
        else:
            raise ValueError(f"unsupported RTL source identity: {name}")
        if manifest["sources"].get(str(source)) != digest:
            raise ValueError(f"RTL reference source closure differs: {name}")
    expected = validate_completion((reference / "run.log").read_text(), workload, cycles)
    ref_bounds = waveform_bounds(reference / "activity.vcd", cycles)
    if len(ref_bounds["accepted_trigger_edges"]) != expected["completed_jobs"]:
        raise ValueError("RTL trigger count differs")
    out.mkdir(parents=True, exist_ok=False)
    inputs = {str(path): sha(path) for path in (cells, primitives, reference / "provenance.json",
              reference / "program.json", reference / "run.log", reference / "activity.vcd",
              reference / "build/stim_instr.txt", reference / "build/stim_data.txt",
              prepared / "synthesis_manifest.json", prepared / "mapped.v")}
    if frozen_receipt is not None:
        # This is an upstream-verified receipt, not permission to substitute a runtime.
        inputs[str(frozen_receipt)] = sha(frozen_receipt)
    compatible = out / "sky130_primitives_functional.v"
    compatible.write_text(functional_primitives(primitives.read_bytes()))
    # The flagged continuous and clocked drivers are in mutually exclusive
    # generate branches / disjoint packed slices. Do not waive other files.
    waiver = out / "cpu_compat.vlt"
    waiver.write_text('`verilator_config\nlint_off -rule BLKANDNBLK -file "*cv32e40p_cs_registers.sv"\n')
    inputs.update({str(compatible): sha(compatible), str(waiver): sha(waiver)})
    # Copy the actual input images, not regenerated software with a different build identity.
    for name in ("stim_instr.txt", "stim_data.txt"):
        (out / name).write_bytes((reference / "build" / name).read_bytes())
    binary = out / "obj/simulate"
    command = [verilator, "--binary", "--trace-fst", "--trace-underscore", "--timing", "--assert",
               "-Wno-fatal", "-Wno-ENUMVALUE", "--top-module", "redmule_tb_wrap",
               "-GHeight=4", "-GWidth=4", "-GEnableReordering=0", "-GPROB_STALL=0",
               "-DFUNCTIONAL", "-DUNIT_DELAY=", "-j", str(jobs), "--Mdir", str(out / "obj"),
               "-o", str(binary), str(waiver), "-f", str(prepared / "replay.vlt"),
               str(prepared / "mapped.v"), str(cells), str(compatible)]
    write_json(out / "invocation.json", command)
    run(command, out / "compile.log")
    run([str(binary), f"+STIM_INSTR={out}/stim_instr.txt", f"+STIM_DATA={out}/stim_data.txt",
         f"+OBSERVATION_CYCLES={cycles}"], out / "run.log", out)
    functional = validate_completion((out / "run.log").read_text(), workload, cycles)
    if functional != expected:
        raise ValueError("mapped reference completions differ from RTL")
    run([fst2vcd, "-o", str(out / "activity.vcd"), str(out / "activity.fst")], out / "convert.log")
    bounds = waveform_bounds(out / "activity.vcd", cycles)
    if bounds != ref_bounds:
        raise ValueError("mapped trigger timing or waveform bounds differ from RTL")
    # Recheck all input hashes before publishing a successful receipt.
    for path, digest in inputs.items():
        if sha(path) != digest:
            raise ValueError(f"input changed during replay: {path}")
    verify_preparation(prepared)
    write_json(out / "functional.json", functional)
    write_json(out / "gls_receipt.json", dict(schema=1, valid=True, inputs=inputs,
        preparation_sha256=sha(prepared / "preparation.json"), parameters=PARAMETERS,
        functional=functional, window=bounds, liberty=manifest["liberty"],
        liberty_sha256=manifest["liberty_sha256"], simulation_model_sha256={
            str(cells): sha(cells), str(primitives): sha(primitives)},
        simulator_version=subprocess.check_output([verilator, "--version"], text=True).strip(),
        simulator_sha256=sha(binary), waveform_sha256=sha(out / "activity.vcd"),
        primitive_compatibility="six pinned UDPs replaced by known-input two-state equivalents",
        memory_policy=manifest["memory_policy"], fidelity="zero-delay mapped functional replay",
        frozen_replay_receipt=str(frozen_receipt) if frozen_receipt else None,
        frozen_measurement_identity="reference provenance retained; no runtime identity alias"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "synthesize", "replay"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-list", type=Path)
    parser.add_argument("--dependency-root", type=Path)
    parser.add_argument("--liberty", type=Path)
    parser.add_argument("--plugin", type=Path)
    parser.add_argument("--yosys", default="yosys")
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--cells", type=Path)
    parser.add_argument("--primitives", type=Path)
    parser.add_argument("--verilator", default="verilator")
    parser.add_argument("--fst2vcd", default="fst2vcd")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--frozen-receipt", type=Path)
    args = parser.parse_args(argv)
    if args.stage == "prepare":
        if not all((args.source_list, args.dependency_root, args.liberty, args.plugin)):
            parser.error("prepare requires source-list, dependency-root, liberty and plugin")
        prepare(args.source_list.resolve(strict=True), args.dependency_root.resolve(strict=True),
                args.out.resolve(), args.liberty.resolve(strict=True), args.plugin.resolve(strict=True))
    elif args.stage == "synthesize":
        synthesize(args.out.resolve(strict=True), args.yosys)
    else:
        if not all((args.prepared, args.reference, args.cells, args.primitives)) or args.jobs < 1:
            parser.error("replay requires prepared, reference, cells, primitives and positive jobs")
        replay(args.prepared.resolve(strict=True), args.reference.resolve(strict=True), args.out.resolve(),
               args.cells.resolve(strict=True), args.primitives.resolve(strict=True),
               args.verilator, args.fst2vcd, args.jobs,
               args.frozen_receipt.resolve(strict=True) if args.frozen_receipt else None)


if __name__ == "__main__":
    main()
