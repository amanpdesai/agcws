"""Reproduce matched GLS and native windows using only the image toolchain."""

import argparse
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path

from analysis.archive_matched_aes_gls import archive as archive_aes
from analysis.archive_matched_dma_gls import archive as archive_dma
from validation.aes_gls import sha
from validation.window_power import evaluate


def replay(inputs, design, out):
    if os.getuid() == 0 or Path("/workspace/src").exists():
        raise ValueError(
            "requires non-root image-only execution, without a host source mount"
        )
    manifest = json.loads((inputs / "inputs.json").read_text())
    for name, digest in manifest["files"].items():
        if sha(inputs / name) != digest:
            raise ValueError("staged input checksum differs")
    case = next(c for c in manifest["cases"] if c["design"] == design)
    root = inputs / design
    rtl, synthesis = root / "rtl", root / "synthesis"
    expected = json.loads((root / "expected_power.json").read_text())
    n = json.loads((rtl / "activity.json").read_text())["clock_edges"]
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    gls = out / "gls"
    command = [os.sys.executable, "-m", f"validation.{design}_gls"]
    if design == "aes":
        command += [
            "replay",
            "--workload",
            str(rtl / "workload.json"),
            "--clock-edges",
            str(n),
        ]
    else:
        command += ["--rtl", str(rtl)]
    command += ["--synthesis", str(synthesis), "--out", str(gls)]
    with (out / "replay.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    actual = evaluate(
        gls / "activity.vcd",
        rtl / "activity.vcd",
        synthesis,
        "clk_i" if design == "aes" else "clk",
        "aes_core_smoke/dut" if design == "aes" else "axi_dma",
        n,
        out / "windows",
    )
    if actual["grid"] != expected["grid"]:
        raise ValueError("container/host grids differ")
    comparisons = []
    for left, right in zip(
        [actual["full"], *actual["windows"]], [expected["full"], *expected["windows"]]
    ):
        for name in ["annotated_pins", "unannotated_pins", "leaf_count"]:
            if left[name] != right[name]:
                raise ValueError("container annotation/structure differs")
        for key in [
            "internal_power_w",
            "switching_power_w",
            "dynamic_power_w",
            "leakage_power_w",
        ]:
            good = math.isclose(
                left[key],
                right[key],
                rel_tol=manifest["power_relative_tolerance"],
                abs_tol=manifest["power_absolute_tolerance_w"],
            )
            comparisons.append(
                {
                    "window": left["name"],
                    "metric": key,
                    "host": right[key],
                    "container": left[key],
                    "matches": good,
                }
            )
    (gls / "power").mkdir()
    shutil.copy2(out / "windows/full.rpt", gls / "power/power.rpt")
    (archive_aes if design == "aes" else archive_dma)(
        rtl, gls, synthesis, out / "matched_replay"
    )
    versions = {}
    for tool, command in {
        "python": [os.sys.executable, "--version"],
        "iverilog": ["iverilog", "-V"],
        "yosys": ["yosys", "-V"],
        "verilator": ["verilator", "--version"],
    }.items():
        versions[tool] = subprocess.run(
            command, capture_output=True, text=True, check=True
        ).stdout.splitlines()[0]
    packages = subprocess.check_output(
        [os.sys.executable, "-m", "pip", "freeze"], text=True
    )
    (out / "python-packages.txt").write_text(packages)
    record = {
        "case": case,
        "image_only": True,
        "uid": os.getuid(),
        "gid": os.getgid(),
        "input_manifest_sha256": sha(inputs / "inputs.json"),
        "comparison": comparisons,
        "all_power_components_match": all(c["matches"] for c in comparisons),
        "wall_clock_s": time.monotonic() - start,
        "source_sha256": sha(Path(__file__)),
        "tool_version": actual["tool_version"],
        "tool_versions": versions,
        "packages_sha256": sha(out / "python-packages.txt"),
    }
    (out / "verification.json").write_text(json.dumps(record, indent=2) + "\n")
    if not record["all_power_components_match"]:
        raise ValueError("host/container power mismatch; diagnostic results retained")
    print("CONTAINER_REPLAY_VERIFIED", design, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--design", choices=["aes", "dma"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    replay(args.inputs, args.design, args.out)
