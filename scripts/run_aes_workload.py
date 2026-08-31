#!/usr/bin/env python3
"""Run the deterministic AES core harness for a validated block workload."""
import argparse
import json
import subprocess
from pathlib import Path

def block_count(workload: dict) -> int:
    operations = workload.get("operations")
    if not isinstance(operations, list) or not operations:
        raise ValueError("workload requires non-empty operations")
    if operations[0].get("op") != "configure":
        raise ValueError("configure must be first")
    total = sum(int(op.get("blocks", 1)) for op in operations[1:] if op.get("op") in {"encrypt", "decrypt"})
    if total < 1 or total > 256:
        raise ValueError("workload must contain 1..256 crypto blocks")
    return total

def idle_cycles(workload: dict) -> int:
    total = sum(int(op.get("cycles", 0)) for op in workload.get("operations", [])
                if op.get("op") == "idle")
    if total < 0 or total > 10000:
        raise ValueError("idle cycles must be in [0,10000]")
    return total

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workload", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out/aes-workload"))
    args = parser.parse_args()
    workload = json.loads(args.workload.read_text())
    blocks = block_count(workload)
    idle = idle_cycles(workload)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "workload.json").write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
    subprocess.run(["bash", "scripts/run_aes_core_smoke.sh", str(args.out), str(blocks), str(idle)], check=True)

if __name__ == "__main__":
    main()
