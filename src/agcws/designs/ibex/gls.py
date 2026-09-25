"""Matched, zero-delay Ibex replay of an existing checked program ELF.

The synthesis boundary is ibex_top, including its FF register file and RVFI.
The unchanged simple-system bus, dual-port RAM, timer and tracer are simulation
collateral outside that boundary. No single-port SRAM model is substituted.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from agcws.core import config
from agcws.core.provenance import file_sha256 as sha
from agcws.designs.ibex.compat import functional_primitives
from agcws.designs.ibex.parameters import verify_parameters, waveform_parameters
from agcws.designs.ibex.programs.activity import markers
from agcws.designs.ibex.programs.feedback import extract as feedback
from agcws.designs.ibex.programs.program import HORIZON, canonical, interpret
from agcws.evaluation.activity.known_bits import Observation, stream_bits
from agcws.evaluation.waveforms.reference_clock import reference_clock_vcd

PARAMETERS = dict(
    BaseIsa="ibex_pkg::BaseIsaRV32IorCHERIoT", RV32E=0,
    RV32M="ibex_pkg::RV32MFast", RV32B="ibex_pkg::RV32BNone",
    RV32ZC="ibex_pkg::RV32ZcaZcbZcmp", RegFile="ibex_pkg::RegFileFF",
    PMPEnable=0, PMPGranularity=0, PMPNumRegions=4, MHPMCounterNum=0,
    MHPMCounterWidth=40, BranchTargetALU=0, WritebackStage=0, ICache=0,
    ICacheECC=0, ICacheTweakInfection=0, BranchPredictor=0, DbgTriggerEn=0,
    SecureIbex=0, LockstepOffset=1, ICacheScramble=0,
    DmBaseAddr="32'h00100000", DmAddrMask="32'h00000003",
    DmHaltAddr="32'h00100000", DmExceptionAddr="32'h00100000",
)
SCOPE = "ibex_gls.system.u_top.u_ibex_top"
CLOCK = "ibex_gls.system.u_top.clk_i"
ASSETS = Path(__file__).with_name("assets")


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def run(command, log, cwd=None):
    with log.open("w") as stream:
        subprocess.run(list(map(str, command)), cwd=cwd, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)


def verify_hashes(inputs):
    for name, expected in inputs.items():
        if sha(Path(name)) != expected:
            raise ValueError(f"input hash mismatch: {name}")


def closure(vc):
    """Use a simulation closure, including its checked elaboration options."""
    vc = vc.resolve(strict=True)
    lines = vc.read_text().splitlines()
    defines, overrides, sources, includes = {}, {}, [], []
    for line in lines:
        if line.startswith("-D"):
            key, _, value = line[2:].partition("=")
            defines[key] = value
        elif line.startswith("-G"):
            key, _, value = line[2:].partition("=")
            overrides[key] = value
        elif line.startswith("+incdir+"):
            includes.append((vc.parent / line[8:]).resolve(strict=True))
        elif line.endswith((".sv", ".v")):
            sources.append((vc.parent / line).resolve(strict=True))
    expected_defines = {k: str(PARAMETERS[k]) for k in ("RV32M", "RV32B", "RV32ZC", "RegFile")}
    expected_defines.update(RVFI="1", INSTR_CYCLE_DELAY="0")
    if defines != expected_defines:
        raise ValueError(f"unsupported simulation defines: {defines}")
    expected_overrides = {k: str(PARAMETERS[k]) for k in (
        "RV32E", "ICache", "ICacheScramble", "ICacheECC", "BranchTargetALU",
        "WritebackStage", "SecureIbex", "BranchPredictor", "DbgTriggerEn", "PMPEnable",
        "PMPGranularity", "PMPNumRegions", "MHPMCounterNum", "MHPMCounterWidth")}
    if overrides != expected_overrides or not sources:
        raise ValueError(f"unsupported simulation parameters: {overrides}")
    includes = sorted(set(includes + [p.parent for p in sources]))
    return sources, includes, defines


def yosys_path(path):
    text = str(path)
    if re.search(r'[\s;"\\]', text):
        raise ValueError(f"unsupported Yosys path: {text}")
    return text


def effective_parameters(mhpm_counter_num=0):
    if type(mhpm_counter_num) is not int or not 0 <= mhpm_counter_num <= 29:
        raise ValueError("MHPM counter count must be an integer in [0,29]")
    return {**PARAMETERS, "MHPMCounterNum": mhpm_counter_num}


def synthesize(vc, out, *, finish_checkpoint=False, mhpm_counter_num=0):
    sources, includes, defines = closure(vc)
    parameters = effective_parameters(mhpm_counter_num)
    plugin = Path(os.environ["AGCWS_SLANG_PLUGIN"]).resolve(strict=True)
    if not plugin.is_file():
        raise ValueError("AGCWS_SLANG_PLUGIN must name the slang shared library")
    liberty = config.LIBERTY.resolve(strict=True)
    # Simulation-only modules (DPI, tracer, system RAM) are not synthesized.
    excluded = {"ibex_simple_system.sv", "ibex_top_tracing.sv", "ibex_tracer.sv",
                "simulator_ctrl.sv", "ram_2p.sv"}
    rtl = [p for p in sources if p.name not in excluded]
    # The pinned top initializes an unused lint sink from input nets. Slang
    # cannot synthesize that variable initializer. A continuous lint sink has
    # no functional fanout; retain all architectural initialization untouched.
    original_top = next(p for p in rtl if p.name == "ibex_top.sv")
    adapted_top = out / "ibex_top.sv"
    top_text = original_top.read_text()
    if top_text.count("logic unused_scramble_inputs =") != 1:
        raise ValueError("unrecognized Ibex unused scramble sink")
    adapted_top.write_text(top_text.replace("logic unused_scramble_inputs =",
                                           "wire unused_scramble_inputs ="))
    rtl = [adapted_top if p == original_top else p for p in rtl]
    read = f"plugin -i {yosys_path(plugin)}; read_slang --top ibex_top -D SYNTHESIS -D RVFI "
    read += " ".join(f"-G {k}={v}" for k, v in parameters.items()) + " "
    read += " ".join(f"-I {yosys_path(p)}" for p in includes) + " "
    read += " ".join(yosys_path(p) for p in rtl)
    script = (read + "; hierarchy -check -top ibex_top; proc; opt; memory; opt; techmap; opt; "
              f"dfflibmap -liberty {yosys_path(liberty)}; abc -liberty {yosys_path(liberty)}; "
              f"clean; check; write_verilog -noattr -noexpr {yosys_path(out / 'mapped.v')}; "
              f"write_json {yosys_path(out / 'mapped.json')}")
    if not finish_checkpoint:
        (out / "synthesis.ys").write_text(script + "\n")
        run([config.YOSYS, "-T", "-s", out / "synthesis.ys"], out / "synthesis.log")
    elif (out / "synthesis.ys").read_text() != script + "\n":
        raise ValueError("synthesis checkpoint command differs")
    latch_map = ASSETS / "latch_map.v"
    checkpoint_hash = sha(out / "mapped.v")
    finish = (f"read_liberty -lib {yosys_path(liberty)}; read_verilog -icells {yosys_path(out / 'mapped.v')}; "
              f"techmap -map {yosys_path(latch_map)}; hierarchy -check -top ibex_top; check -assert; "
              f"write_verilog -noattr -noexpr {yosys_path(out / 'mapped-final.v')}; "
              f"write_json {yosys_path(out / 'mapped.json')}")
    run([config.YOSYS, "-T", "-p", finish], out / "latch-map.log")
    (out / "mapped-final.v").replace(out / "mapped.v")
    mapped = json.loads((out / "mapped.json").read_text())
    cells = mapped["modules"]["ibex_top"]["cells"]
    unexpected = sorted({c["type"] for c in cells.values()
                         if not c["type"].startswith("sky130_fd_sc_hd__")})
    if unexpected:
        raise ValueError(f"unmapped cells or unsupported macros: {unexpected}")
    # Headers are part of the elaboration identity, not just source files.
    inputs = set(sources + [vc.resolve(), adapted_top, latch_map])
    for directory in includes:
        inputs.update(directory.glob("*.svh"))
        inputs.update(directory.glob("*.vh"))
    write(out / "manifest.json", {
        "schema": "ibex-matched-gls-v1", "top": "ibex_top", "parameters": parameters,
        "configuration_override": {"MHPMCounterNum": mhpm_counter_num},
        "defines": defines, "closure": str(vc.resolve()),
        "sources": {str(p): sha(p) for p in sorted(inputs)},
        "netlist_sha256": sha(out / "mapped.v"), "liberty": str(liberty),
        "liberty_sha256": sha(liberty), "power_libraries": {str(liberty): sha(liberty)},
        "plugin_sha256": sha(plugin), "mapped_cell_count": len(cells),
        "driver_sha256": sha(Path(__file__)),
        "pre_latch_mapping_sha256": checkpoint_hash,
        "frontend_adaptation": "unused_scramble_inputs variable initializer to continuous wire; unused lint sink only",
        "memory_macros": [], "memory_policy": "FF register file; ICache disabled; inferred ROMs lowered to gates",
        "external_memory": {"module": "prim_ram_2p", "depth": 262144, "width": 32,
                            "ports": "two synchronous ports; byte writes; read-before-write",
                            "power_included": False, "liberty": None},
        "power_scope": "ibex_top including RVFI instrumentation; excludes system RAM/bus/timer/tracer",
        "power_limitations": "RVFI instrumentation is synthesized and contributes power; no uninstrumented core power claim. RTL proxy excludes CSRs and register file and has a different net inventory.",
        "yosys_version": subprocess.check_output([str(config.YOSYS), "-V"], text=True).strip(),
    })


def system_harness(text):
    """Drop only C++ performance-counter accessors, which name RTL internals."""
    prefix, separator, tail = text.partition('  export "DPI-C" function mhpmcounter_num;')
    if not separator or not tail.rstrip().endswith("endmodule"):
        raise ValueError("unrecognized simple-system DPI layout")
    return prefix + "endmodule\n"


def tracing_harness(text):
    result, count = re.subn(r"ibex_top #\(.*?\) u_ibex_top \(",
                            "ibex_top u_ibex_top (", text, flags=re.S)
    if count != 1:
        raise ValueError("unrecognized tracing wrapper")
    # Slang flattens unpacked output arrays with element zero at the LSB.
    for port in ("rvfi_ext_mhpmcounters", "rvfi_ext_mhpmcountersh"):
        packed = "{" + ", ".join(f"{port}[{i}]" for i in reversed(range(10))) + "}"
        result = result.replace(f".{port},", f".{port}({packed}),")
    holds = []
    for port, width in (("instr_rvalid_i", 1), ("instr_rdata_i", 32),
                        ("data_rvalid_i", 1), ("data_rdata_i", 32), ("data_err_i", 1)):
        holds.append(f"logic [{width-1}:0] gls_{port};\n  always @(negedge clk_i) gls_{port} <= {port};")
        result = result.replace(f".{port},", f".{port}(gls_{port}),", 1)
    result = result.replace("ibex_top u_ibex_top (", "\n".join(holds) + "\n  ibex_top u_ibex_top (")
    return result


def checked_reference(root, *, frozen_receipt=None):
    functional = json.loads((root / "functional.json").read_text())
    program = canonical(json.loads((root / "program.json").read_text()))
    if functional.get("functional_ok") is not True or functional["expected"] != interpret(program):
        raise ValueError("RTL functional reference is not valid for this program")
    # Frozen input paths are an identity assertion. A moved file with the same
    # basename is not permission to silently rebase the frozen measurement.
    if frozen_receipt is None:
        verify_hashes(functional["inputs"])
    else:
        receipt = json.loads(frozen_receipt.read_text())
        profile = json.loads((root / 'profile.json').read_text())
        frozen_binding(frozen_receipt, root, functional, profile)
        inputs = {}
        for name, digest in functional['inputs'].items():
            path = Path(name)
            if '..' in path.parts:
                raise ValueError('unsafe frozen Ibex input path')
            if path.is_relative_to('/workspace/out'):
                mapped = frozen_receipt.parent / path.relative_to('/workspace/out')
            elif path.is_relative_to('/workspace/src'):
                mapped = Path(receipt['runtime']) / path.relative_to('/workspace')
            elif not path.is_absolute() and path.parts[0] == 'src':
                mapped = Path(receipt['runtime']) / path
            else:
                raise ValueError(f'undeclared frozen Ibex input mount: {name}')
            inputs[str(mapped)] = digest
        verify_hashes(inputs)
    # Check original recorded executable artifacts without remapping their identity.
    for name in ("program.S", "program.elf", "loadable.bin"):
        matches = [v for k, v in functional["inputs"].items() if Path(k).name == name]
        if len(matches) != 1 or sha(root / name) != matches[0]:
            raise ValueError(f"RTL recorded artifact differs: {name}")
    found, _ = markers(root / "trace_core_00000000.log", functional["marker_pcs"])
    bounds = marker_bounds(found)
    profile = json.loads((root / "profile.json").read_text())
    if (profile["timescale"], profile["period_ticks"], profile["clock_edges"]) != ("1ps", 2, HORIZON):
        raise ValueError("unsupported RTL waveform clock")
    if [profile["begin_tick"], profile["end_tick"]] != bounds:
        raise ValueError("RTL profile differs from retirement markers")
    if sha(root / "sim.fst") != profile["waveform_sha256"]:
        raise ValueError("RTL waveform differs from checked profile")
    return functional, profile, bounds


def marker_bounds(found):
    begin = found["measure_start"]["tick"]
    end = begin + 2 * HORIZON
    if not begin < found["body_complete"]["tick"] < end < found["measure_stop"]["tick"]:
        raise ValueError("useful work or observation window did not complete in time")
    return [begin, end]


def compare_retirement(rtl, gls, rtl_begin, gls_begin):
    """Compare every retired PC/word and its relative cycle, through program halt."""
    from itertools import zip_longest
    with rtl.open() as a, gls.open() as b:
        next(a)
        next(b)
        for index, (left, right) in enumerate(zip_longest(a, b)):
            if left is None or right is None:
                raise ValueError("RTL/GLS retirement count differs")
            x, y = left.split(), right.split()
            if (int(x[0]) - rtl_begin, x[2:4]) != (int(y[0]) - gls_begin, y[2:4]):
                raise ValueError(f"RTL/GLS retirement differs at row {index}")


def frozen_binding(receipt_path, rtl, functional, profile):
    """Bind a binary-only frozen replay explicitly, never infer a missing build file."""
    receipt_path = receipt_path.resolve(strict=True)
    receipt = json.loads(receipt_path.read_text())
    root = receipt_path.parent
    request_path, result_path = root / 'replay-request.json', root / 'replay-result.json'
    verify_hashes({str(request_path): receipt['request_sha256'],
                   str(result_path): receipt['result_sha256']})
    request, result = json.loads(request_path.read_text()), json.loads(result_path.read_text())
    if (request['manifest']['spec']['domain'] != 'ibex-temporal' or not result['valid']
            or result['profile'] != profile
            or result['profile']['window_rates'] != request['case']['rates']
            or json.loads((rtl / 'program.json').read_text()) != request['case']['program']):
        raise ValueError('frozen Ibex replay does not match the selected workload')
    binaries = [digest for path, digest in functional['inputs'].items()
                if Path(path).name == 'Vibex_simple_system']
    if binaries != [request['manifest']['runtime']['binary_sha256']]:
        raise ValueError('frozen Ibex binary identity differs')
    return {'receipt_sha256': sha(receipt_path), 'binary_sha256': binaries[0],
            'configuration_source': 'parameters emitted by the verified original simulator waveform',
            'limitation': 'Original build .vc was not retained; source-build equivalence is not claimed'}


def replay(synthesis, rtl, out, jobs=2, *, frozen_receipt=None):
    synthesis, rtl = synthesis.resolve(strict=True), rtl.resolve(strict=True)
    manifest = json.loads((synthesis / "manifest.json").read_text())
    parameters = effective_parameters(manifest['parameters']['MHPMCounterNum'])
    if manifest.get("schema") != "ibex-matched-gls-v1" or manifest["parameters"] != parameters:
        raise ValueError("not a matched Ibex synthesis")
    verify_hashes(manifest["sources"])
    verify_hashes(manifest["power_libraries"])
    verify_hashes({str(synthesis / "mapped.v"): manifest["netlist_sha256"]})
    functional, profile, rtl_bounds = checked_reference(rtl, frozen_receipt=frozen_receipt)
    recorded_simulators = [Path(p) for p in functional["inputs"]
                           if Path(p).name == "Vibex_simple_system"]
    if len(recorded_simulators) != 1:
        raise ValueError("RTL reference lacks its pinned simple-system simulator")
    runtime_vc = recorded_simulators[0].parent / "lowrisc_ibex_ibex_simple_system_0.vc"
    binding = None
    if frozen_receipt is not None:
        binding = frozen_binding(frozen_receipt, rtl, functional, profile)
    elif sha(runtime_vc) != sha(Path(manifest["closure"])):
        raise ValueError("RTL simulator closure differs from synthesis closure")
    rtl_waveform = out / 'rtl.vcd'
    with rtl_waveform.open('w') as stream:
        subprocess.run([str(config.FST2VCD), str(rtl / 'sim.fst')], stdout=stream, check=True)
    with rtl_waveform.open() as stream:
        observed = waveform_parameters(stream, 'TOP.ibex_simple_system.u_top.u_ibex_top')
    numeric_parameters = verify_parameters(observed, parameters)
    sources, includes, defines = closure(Path(manifest["closure"]))
    models = [Path(os.environ[k]).resolve(strict=True) for k in
              ("AGCWS_SKY130_CELL_MODELS", "AGCWS_SKY130_PRIMITIVES")]
    original_primitives = models[1]
    models[1] = out / 'sky130_primitives_functional.v'
    models[1].write_text(functional_primitives(original_primitives.read_bytes()))
    simulation = []
    for source in sources:
        if source.name == "ibex_top.sv":
            simulation.append(synthesis / "mapped.v")
        elif source.name in ("ibex_simple_system.sv", "ibex_top_tracing.sv"):
            target = out / source.name
            transform = system_harness if source.name == "ibex_simple_system.sv" else tracing_harness
            target.write_text(transform(source.read_text()))
            simulation.append(target)
        else:
            simulation.append(source)
    data = (rtl / "loadable.bin").read_bytes()
    if len(data) > 1024 * 1024 or len(data) % 4:
        raise ValueError("unsupported RAM image geometry")
    (out / "program.vmem").write_text("@00000000\n" + "\n".join(
        f"{int.from_bytes(data[i:i+4], 'little'):08x}" for i in range(0, len(data), 4)) + "\n")
    retirement_rows = []
    with (rtl / "trace_core_00000000.log").open() as stream:
        next(stream)
        for line in stream:
            row = line.split()
            retirement_rows.append(f"{int(row[0]):08x}{int(row[2], 16):08x}{int(row[3], 16):08x}")
    if not 0 < len(retirement_rows) <= 1048576:
        raise ValueError("reference retirement trace exceeds scoreboard capacity")
    (out / "retirement.vmem").write_text("\n".join(retirement_rows) + "\n")
    build = out / "obj"
    command = [config.VERILATOR, "--binary", "--timing", "--trace-fst", "--trace-structs", "--trace-underscore",
               "--trace-max-array", "1024", "--top-module", "ibex_gls", "--Mdir", build,
               "-j", str(jobs), "-Wno-fatal", "--timescale", "1ps/1ps", "-DFUNCTIONAL",
               "-DDISABLE_PRIM_CDC_RAND_DELAY", "--unroll-count", "72",
               f"-DAGCWS_MHPM_COUNTER_NUM={parameters['MHPMCounterNum']}",
               "-DUNIT_DELAY=", *[f"-D{k}={v}" for k, v in defines.items()],
               *[f"-I{p}" for p in includes], *simulation, *models, ASSETS / "gls.sv"]
    run(command, out / "compile.log")
    run([build / "Vibex_gls", f"+RETIREMENTS={len(retirement_rows)}"], out / "run.log", cwd=out)
    match = re.search(r"AGCWS_STATE ([0-9A-Fa-f ]+)\n", (out / "ibex_simple_system.log").read_text())
    if not match or [int(v, 16) for v in match[1].split()] != functional["expected"]["registers"] + functional["expected"]["memory"]:
        raise ValueError("architectural reference mismatch")
    found, retired = markers(out / "trace_core_00000000.log", functional["marker_pcs"])
    marker_window = marker_bounds(found)
    # The C++ reference prints retirement one tick after its waveform edge.
    # The SV tracer prints at the edge itself. Observe the same post-marker
    # cycles, not the marker edge in one tier and the next edge in the other.
    bounds = [tick + 1 for tick in marker_window]
    compare_retirement(rtl / "trace_core_00000000.log", out / "trace_core_00000000.log",
                       rtl_bounds[0], marker_window[0])
    write(out / "functional.json", {**functional, "replay": "GLS", "rtl_functional_sha256": sha(rtl / "functional.json")})
    write(out / "feedback.json", feedback(out))
    with (out / "activity.vcd").open("w") as stream:
        subprocess.run([str(config.FST2VCD), str(out / "sim.fst")], stdout=stream, check=True)
    with (out / "activity.vcd").open() as stream:
        activity = stream_bits(stream, Observation(SCOPE, CLOCK, HORIZON, begin=bounds[0],
                               end=bounds[1], period=2, require_known_initial=True))
    activity.pop("per_cycle_toggles")
    write(out / "activity.json", activity)
    write(out / "receipt.json", {
        "schema": "ibex-matched-gls-v1", "functional_ok": True,
        "retirement_matched": True, "retired_instructions": retired,
        "parameters": parameters, "observed_rtl_parameters": numeric_parameters,
        "frozen_binding": binding, "markers": found,
        "rtl_bounds": rtl_bounds, "gls_bounds": bounds, "bounds_semantics": "[begin,end)",
        "gls_marker_to_window_offset_ticks": 1,
        "bounds_units": "native waveform ticks", "rtl_waveform_sha256": profile["waveform_sha256"],
        "clock": CLOCK, "rtl_clock": "TOP.ibex_simple_system.u_top.clk_i",
        "scope": SCOPE, "sta_scope": SCOPE.removeprefix("TOP.").replace(".", "/"),
        "rtl_proxy_scope": profile["scope"], "rtl_proxy_exclusions": profile["exclusions"],
        "timescale": "1ps", "period_ticks": 2, "expected_clock_period_s": 2e-12,
        "clock_edges": HORIZON, "bin_cycles": [HORIZON // 8] * 8,
        "power_libraries": manifest["power_libraries"], "memory_macros": manifest["memory_macros"],
        "external_memory": manifest["external_memory"], "power_scope": manifest["power_scope"],
        "power_limitations": manifest["power_limitations"],
        "simulation_models": {str(p): sha(p) for p in models},
        "simulation_binary_sha256": sha(build / 'Vibex_gls'),
        "primitive_compatibility": {
            "original": str(original_primitives), "original_sha256": sha(original_primitives),
            "derived_sha256": sha(models[1]),
            "contract": "Icarus-checked known-input two-state equivalence; no four-state or SDF claim"},
        "inputs": {str(p): sha(p) for p in [synthesis / "manifest.json", synthesis / "mapped.v",
                   rtl / "functional.json", rtl / "profile.json", rtl / "program.json",
                   rtl / "program.elf", rtl / "loadable.bin", rtl / "trace_core_00000000.log",
                   ASSETS / "gls.sv", Path(__file__).resolve(),
                   Path(__file__).with_name('compat.py'),
                   Path(__file__).parents[1] / 'redmule/compat.py', *simulation]},
        "waveform_sha256": sha(out / "activity.vcd"),
        "claim": "Reference-checked zero-delay gate replay; no power result or timing closure claim",
    })


def replay_trial(rtl: Path, synthesis: Path, out: Path, *, frozen_receipt=None) -> dict:
    """Shared-dispatcher adapter; never mutates or restores the original trial."""
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    options = {'frozen_receipt': frozen_receipt} if frozen_receipt is not None else {}
    replay(synthesis, rtl, out, **options)
    receipt = json.loads((out / "receipt.json").read_text())
    rtl_waveform = out / "rtl.vcd"
    if not rtl_waveform.exists():
        with rtl_waveform.open("w") as stream:
            subprocess.run([str(config.FST2VCD), str(rtl.resolve() / "sim.fst")],
                           stdout=stream, check=True)
    gls_power, rtl_power = out / "power_gls.vcd", out / "power_rtl.vcd"
    conversions = [reference_clock_vcd(out / "activity.vcd", gls_power, 5000),
                   reference_clock_vcd(rtl_waveform, rtl_power, 5000)]
    bounds = [tick * 5000 for tick in receipt["gls_bounds"]]
    rtl_bounds = [tick * 5000 for tick in receipt["rtl_bounds"]]
    write(out / "power_clock.json", {
        "schema": "ibex-reference-clock-v1", "conversions": conversions,
        "native_receipt_sha256": sha(out / "receipt.json"),
        "native_period_s": 2e-12, "expected_period_s": 1e-8,
        "native_bounds": receipt["gls_bounds"], "bounds": bounds,
        "native_rtl_bounds": receipt["rtl_bounds"], "rtl_bounds": rtl_bounds,
        "clock_edges": HORIZON, "clock": receipt["clock"],
        "rtl_clock": receipt["rtl_clock"], "scope": receipt["sta_scope"],
        "claim": "Declared 10ns power reference clock; exact integer timestamp scaling, not physical timing closure; frozen native RTL activity unchanged",
    })
    return {"waveform": gls_power, "rtl_waveform": rtl_power,
            "clock": receipt["clock"], "rtl_clock": receipt["rtl_clock"],
            "scope": receipt["sta_scope"], "clock_port": "clk_i",
            "clock_edges": HORIZON, "bounds": bounds, "rtl_bounds": rtl_bounds,
            "expected_period_s": 1e-8}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("synthesize", "replay"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--closure", type=Path)
    parser.add_argument("--synthesis", type=Path)
    parser.add_argument("--rtl", type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--mhpm-counter-num", type=int, default=0)
    args = parser.parse_args(argv)
    if args.stage == "synthesize" and not args.closure:
        parser.error("synthesize requires --closure (the pinned simulation .vc)")
    if args.stage == "replay" and not (args.synthesis and args.rtl):
        parser.error("replay requires --synthesis and --rtl")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if args.stage == "synthesize":
        synthesize(args.closure, out, mhpm_counter_num=args.mhpm_counter_num)
    else:
        replay(args.synthesis, args.rtl, out, args.jobs)


if __name__ == "__main__":
    main()
