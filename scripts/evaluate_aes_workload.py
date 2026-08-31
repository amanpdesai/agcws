#!/usr/bin/env python3
"""Evaluate one legal AES workload through simulation and OpenSTA."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from agcws.adapters.aes import AESAdapter
from agcws.nodes.power import parse_opensta_power_file
from agcws.nodes.validation import validate_static


def evaluate(workload_path: Path, synthesis_dir: Path, output_dir: Path) -> dict:
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
    subprocess.run(
        ["bash", "scripts/run_opensta_aes.sh", str(synthesis_dir),
         str(output_dir / "activity.vcd"), str(output_dir / "opensta")],
        check=True,
    )
    profile = parse_opensta_power_file(output_dir / "opensta/power.rpt")
    result = {
        "valid": True,
        "useful_work": int(match.group(1)),
        "mean_power": profile.mean_power,
        "fidelity": profile.fidelity,
        "activity": json.loads((output_dir / "activity.json").read_text()),
    }
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", type=Path)
    parser.add_argument("synthesis_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-evaluation"))
    args = parser.parse_args()
    print(json.dumps(evaluate(args.workload, args.synthesis_dir, args.out), indent=2))


if __name__ == "__main__":
    main()
