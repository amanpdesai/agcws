#!/usr/bin/env python3
"""Evaluate one legal AES workload through simulation and OpenSTA."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agcws.adapters.aes import AESAdapter
from agcws.nodes.power import parse_annotation_summary, parse_opensta_power_file
from agcws.nodes.validation import validate_static
from agcws.adapters.base import SimResult
from agcws.provenance import input_record, toolchain_record
from agcws.nodes.activity import attribute_regions
from agcws import config


def evaluate(workload_path: Path, synthesis_dir: Path, output_dir: Path, *, allow_invalid: bool = False) -> dict:
    workload = json.loads(workload_path.read_text())
    validity = validate_static(AESAdapter(), workload)
    if not validity.valid:
        raise ValueError(f"invalid workload at {validity.stage.value}: {validity.reason}")
    output_dir.mkdir(parents=True, exist_ok=True)
    workload_copy = output_dir / "workload.json"
    workload_copy.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
    subprocess.run(
        [sys.executable, "scripts/run_aes_workload.py", str(workload_path), "--out", str(output_dir)],
        check=True,
    )
    log = (output_dir / "run.log").read_text()
    match = re.search(r"AES_CORE_WORKLOAD_DONE blocks=(\d+)", log)
    if not match:
        raise RuntimeError("simulation log has no completed-work marker")
    completed_blocks = int(match.group(1))
    runtime_validity = AESAdapter().validate_result(
        SimResult(terminated=True, assertions_ok=True, outputs_ok=True,
                  useful_work=completed_blocks)
    )
    if not runtime_validity.valid:
        if not allow_invalid:
            raise ValueError(f"invalid simulated workload at {runtime_validity.stage.value}: {runtime_validity.reason}")
        result = {"valid": False, "useful_work": completed_blocks,
                  "invalid_stage": runtime_validity.stage.value,
                  "invalid_reason": runtime_validity.reason,
                  "activity": json.loads((output_dir / "activity.json").read_text())}
        (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    subprocess.run(
        ["bash", "scripts/run_opensta_aes.sh", str(synthesis_dir),
         str(output_dir / "activity.vcd"), str(output_dir / "opensta")],
        check=True,
    )
    profile = parse_opensta_power_file(output_dir / "opensta/power.rpt")
    annotation_text = (output_dir / "opensta/power.rpt").read_text()
    annotation = parse_annotation_summary(annotation_text)
    if annotation is None:
        raise RuntimeError("OpenSTA report has no parseable activity annotation count")
    activity = json.loads((output_dir / "activity.json").read_text())
    by_region = attribute_regions(activity["signal_transitions"], AESAdapter.activity_region_prefixes)
    result = {
        "valid": True,
        "useful_work": completed_blocks,
        "mean_power": profile.mean_power,
        "per_cycle_toggles": activity["per_cycle_toggles"],
        "by_region": by_region,
        "region_fidelity": "activity",
        "fidelity": profile.fidelity,
        "activity": json.loads((output_dir / "activity.json").read_text()),
        "provenance": {
            # Keep provenance portable: artifact paths are interpreted relative
            # to the task directory/repository, while hashes identify content.
            "synthesis_manifest": "synthesis/manifest.json",
            "power_report": "opensta/power.rpt",
            "annotation_report": "opensta/annotation.rpt",
            "annotation": annotation,
            "power_metric": "opensta_total_power_w",
            "liberty": json.loads((synthesis_dir / "manifest.json").read_text()).get("liberty"),
            "tools": toolchain_record({
                "verilator": (config.VERILATOR, ("--version",)),
                "yosys": (config.YOSYS, ("--version",)),
                "opensta": (config.OPENSTA, ("-version",)),
            }),
            "inputs": input_record({
                # Hash the normalized copy that is shipped with the result,
                # not the caller's source file.  This keeps verification
                # valid when JSON formatting differs between the input and
                # the archived workload.
                "workload": workload_copy,
                "synthesis_manifest": synthesis_dir / "manifest.json",
                "activity": output_dir / "activity.json",
                "waveform": output_dir / "activity.vcd",
            }),
        },
    }
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", type=Path)
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-evaluation"))
    parser.add_argument("--allow-invalid", action="store_true")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.workload, args.synthesis_dir, args.out,
                              allow_invalid=args.allow_invalid), indent=2))


if __name__ == "__main__":
    main()
