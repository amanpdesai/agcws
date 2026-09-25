"""Replay one frozen finalist: reference-checked RTL -> GLS -> windowed OpenSTA."""

import argparse
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

from agcws.core import config
from agcws.designs.aes.gls import sha
from agcws.designs.temporal_registry import backend
from agcws.evaluation.power.frozen import replay as replay_frozen
from agcws.evaluation.power.frozen import verify_sources
from agcws.evaluation.power.windows import evaluate
from agcws.evidence.retention import compact
from agcws.studies.finalists import SUPPORTED, read, verify

DRIVERS = {"ibex-temporal": "ibex.gls", "mesh-temporal": "mesh.gls",
           "redmule-temporal": "redmule.container", "redmule-temporal-long": "redmule.container"}


def reconstruction_policy(case):
    """Require strict reconstruction unless a frozen case explicitly requests proof."""
    policy = case.get('reconstruction_policy', 'strict')
    if policy not in ('strict', 'slew-verified-v1'):
        raise ValueError('unknown frozen reconstruction policy')
    if policy != 'strict' and case['domain'] not in ('ibex-temporal', 'redmule-temporal-long'):
        raise ValueError('qualified reconstruction policy requires a supported design')
    return policy


def restore(vcd):
    if vcd.exists():
        return vcd
    receipt = read(vcd.with_suffix(".vcd.retention.json"))
    retained = vcd.parent / receipt["retained"]
    if retained.parent != vcd.parent or sha(retained) != receipt["retained_sha256"]:
        raise ValueError("retained waveform checksum/path differs")
    commands = {"zstd": ["zstd", "-qdc", str(retained)],
                "fst": [str(config.FST2VCD), str(retained)]}
    pending = vcd.with_suffix(".vcd.restoring")
    with pending.open("xb") as stream:
        subprocess.run(commands[receipt["encoding"]], stdout=stream, check=True)
    if sha(pending) != receipt["sha256"] or pending.stat().st_size != receipt["bytes"]:
        raise ValueError("restored VCD differs")
    pending.rename(vcd)
    return vcd


def verify_synthesis_sources(mapped):
    sources = mapped.get('sources')
    if not sources:
        raise ValueError('synthesis lacks RTL source hashes; regenerate with the current synthesis driver')
    root = Path(mapped['source_root']).resolve(strict=True) if 'source_root' in mapped else None
    for name, expected in sources.items():
        path = Path(name)
        if root is not None:
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('unsafe relative synthesis source')
            path = root / path
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f'synthesized RTL source differs: {name}')


def run(plan, case_id, synthesis, out, minimum_coverage=0.99, runtime=None):
    if not 0 < minimum_coverage <= 1:
        raise ValueError("annotation threshold must be in (0,1]")
    verify(plan)
    case = next(c for c in plan["cases"] if c["id"] == case_id)
    domain = case["domain"]
    if domain not in SUPPORTED:
        raise NotImplementedError(f"no validated matched GLS driver for {domain}")
    selected_reconstruction = reconstruction_policy(case)
    manifest = read(Path(case["root"]) / "manifest.json")
    if runtime is not None:
        runtime = verify_sources(manifest, runtime)
    else:
        try:
            verify_sources(manifest, config.ROOT)
        except ValueError as exc:
            raise ValueError(f'replay requires the frozen source checkout: {exc}') from exc
        runtime = config.ROOT
    synthesis = synthesis.resolve(strict=True)
    mapped = read(synthesis / "manifest.json")
    if mapped.get("memory_manifest") or mapped.get("memory_libmap"):
        raise ValueError("macro-mapped netlists require a separately validated macro simulation/power driver")
    if domain.startswith('redmule-'):
        importlib.import_module('agcws.designs.redmule.container').verify_synthesis(synthesis)
    else:
        verify_synthesis_sources(mapped)
    if sha(synthesis / "mapped.v") != mapped["netlist_sha256"]:
        raise ValueError("netlist differs from synthesis manifest")
    if sha(config.LIBERTY) != mapped["liberty_sha256"]:
        raise ValueError("configured Liberty differs from mapped library")
    model_variables = () if domain.startswith('redmule-') else (
        "AGCWS_SKY130_CELL_MODELS", "AGCWS_SKY130_PRIMITIVES")
    for variable in model_variables:
        if not os.environ.get(variable):
            raise ValueError(f"set {variable} to the Sky130 functional simulation collateral")
        Path(os.environ[variable]).resolve(strict=True)
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    request = {"plan_sha256": plan["sha256"], "case": case,
               "reconstruction_policy": selected_reconstruction,
               "synthesis_manifest_sha256": sha(synthesis / "manifest.json"),
               "minimum_pin_annotation_fraction": minimum_coverage,
               "measurement_runtime": str(runtime) if runtime else str(Path.cwd()),
               "validation_sources": {str(p): sha(p) for p in sorted(
                   Path("src/agcws/evaluation/power").glob("*.py"))}}
    (out / "request.json").write_text(json.dumps(request, indent=2) + "\n")
    design = backend(domain)
    scratch = out / "rtl"
    measured = replay_frozen(case, manifest, runtime, scratch)
    if not measured["valid"] or measured["rates"] != case["rates"]:
        raise ValueError("fresh functional RTL replay differs from selected activity")
    if domain not in DRIVERS and (measured["profile"]["timescale"] != "1ps"
                                  or measured["profile"]["period_ticks"] != 10000):
        raise ValueError("current Sky130 replay drivers require a 10 ns clock with 1 ps ticks")
    cache = scratch / "cache" / measured["cache_id"]
    attempts = [cache / "run"] if domain == "ibex-temporal" else list(cache.glob("attempt-*"))
    if len(attempts) != 1:
        raise ValueError("expected exactly one fresh RTL replay")
    rtl = attempts[0]
    rtl_waveform = None if domain == "ibex-temporal" else restore(rtl / "activity.vcd")
    gls = out / "gls"
    if domain in DRIVERS:
        driver = importlib.import_module(f"agcws.designs.{DRIVERS[domain]}")
        driver_options = {}
        if (domain.startswith('redmule-') or domain == 'ibex-temporal') and runtime is not None:
            driver_options['frozen_receipt'] = scratch / 'replay-receipt.json'
        prepared = driver.replay_trial(rtl, synthesis, gls, **driver_options)
        rtl_waveform, waveform = Path(prepared["rtl_waveform"]), Path(prepared["waveform"])
        options = {k: prepared[k] for k in ("rtl_clock", "bounds", "rtl_bounds", "expected_period_s", "clock_port")
                   if k in prepared}
        if domain == 'ibex-temporal' or 'reconstruction_policy' in case:
            options['reconstruction_policy'] = selected_reconstruction
        power = evaluate(waveform, rtl_waveform, synthesis, prepared["clock"],
                         prepared["scope"], prepared["clock_edges"], out / "power", **options)
    else:
        aes = domain == "aes-temporal"
        command = [sys.executable, "-m", "agcws.designs.aes.gls" if aes else "agcws.designs.dma.gls"]
        if aes:
            command += ["replay", "--workload", str(rtl / "workload.json"),
                        "--clock-edges", str(design.clock_edges)]
        else:
            command += ["--rtl", str(rtl)]
        command += ["--synthesis", str(synthesis), "--out", str(gls)]
        with (out / "gls.log").open("w") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        waveform = gls / "activity.vcd"
        options = ({'reconstruction_policy': selected_reconstruction}
                   if 'reconstruction_policy' in case else {})
        power = evaluate(waveform, rtl_waveform, synthesis,
                         "clk_i" if aes else "clk", "aes_core_smoke/dut" if aes else "axi_dma",
                         design.clock_edges, out / "power", **options)
    fractions = [r["annotated_pins"] / (r["annotated_pins"] + r["unannotated_pins"])
                 for r in [power["full"], *power["windows"]]]
    if min(fractions) < minimum_coverage:
        raise ValueError(f"pin annotation coverage below declared threshold: {min(fractions)}")
    result = {"version": "finalist-power-v1", "case_id": case_id,
              "plan_sha256": plan["sha256"], "activity": case,
              "gate_dynamic_power_w": [r["dynamic_power_w"] for r in power["windows"]],
              "gate_dynamic_energy_j": [r["dynamic_power_w"] * duration for r, duration
                                        in zip(power["windows"], power["grid"]["durations_s"])],
              "pin_annotation_fractions": fractions, "power": power,
              "claim": "Zero-delay mapped-gate dynamic power; not signoff or activity-target power accuracy."}
    (out / "measurement.json").write_text(json.dumps(result, indent=2) + "\n")
    with (out / "measurement.json").open("rb") as checkpoint:
        os.fsync(checkpoint.fileno())
    # Lossless retirement only after the durable measurement exists; failures retain diagnostics.
    for trace in sorted(set((rtl_waveform, waveform)) | set(out.rglob('*.vcd'))):
        compact(trace)
    (out / "complete.json").write_text(json.dumps({"measurement_sha256": sha(out / "measurement.json")}) + "\n")
    return result


def main(argv=None):
    config._load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--synthesis", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--minimum-coverage", type=float, default=0.99)
    parser.add_argument("--runtime", type=Path,
                        help="Verified measurement checkout recorded by the study")
    args = parser.parse_args(argv)
    result = run(read(args.plan), args.case, args.synthesis, args.out,
                 args.minimum_coverage, args.runtime)
    print(json.dumps({"case": result["case_id"], "dynamic_power_w": result["gate_dynamic_power_w"]}))


if __name__ == "__main__":
    main()
