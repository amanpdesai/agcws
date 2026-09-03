#!/usr/bin/env python3
"""Compare RTL activity and GLS/OpenSTA on bounded AES workload projections."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
from agcws.analysis.rank_agreement import rank_agreement


def project(workload: dict, max_blocks: int) -> dict:
    remaining = max_blocks
    operations = [workload["operations"][0]]
    for operation in workload["operations"][1:]:
        item = dict(operation)
        if item.get("op") in {"encrypt", "decrypt"}:
            blocks = min(remaining, int(item.get("blocks", 1)))
            if blocks <= 0:
                break
            item["blocks"] = blocks
            remaining -= blocks
        operations.append(item)
        if remaining == 0:
            break
    return {"data_pattern": workload.get("data_pattern", 0), "operations": operations}


def power_watts(report: Path) -> float:
    text = report.read_text()
    match = re.search(r"^Total\s+\S+\s+\S+\s+\S+\s+([0-9.eE+-]+)", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"OpenSTA total power not found in {report}")
    return float(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("synthesis", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-blocks", type=int, default=4)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    workloads = [path for path in sorted(args.corpus.glob("*.json"))
                 if isinstance(json.loads(path.read_text()).get("operations"), list)]
    if args.limit:
        workloads = workloads[:args.limit]
    if len(workloads) < 2:
        raise SystemExit("corpus must contain at least two workloads")
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, source in enumerate(workloads):
        workload = project(json.loads(source.read_text()), args.max_blocks)
        item_dir = args.out / f"workload-{index:03d}"
        rtl_dir, gls_dir, sta_dir = item_dir / "rtl", item_dir / "gls", item_dir / "sta"
        item_dir.mkdir(parents=True, exist_ok=True)
        projected = item_dir / "workload.json"
        projected.write_text(json.dumps(workload, indent=2, sort_keys=True) + "\n")
        started = time.monotonic()
        subprocess.run(["python3", "scripts/run_aes_workload.py", str(projected), "--out", str(rtl_dir)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        rtl = json.loads((rtl_dir / "activity.json").read_text())
        rtl_time = time.monotonic() - started
        started = time.monotonic()
        subprocess.run(["bash", "scripts/run_aes_gls.sh", str(args.synthesis), str(gls_dir), str(projected)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        environment = dict(__import__("os").environ)
        environment["AGCWS_VCD_SCOPE"] = "aes_core_gls/dut"
        subprocess.run(["bash", "scripts/run_opensta_aes.sh", str(args.synthesis), str(gls_dir / "activity.vcd"), str(sta_dir)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, env=environment)
        rows.append({"workload": source.name, "projected_blocks": args.max_blocks,
                     "rtl_transitions_per_cycle": rtl["total_transitions"] / rtl["clock_edges"],
                     "gate_power_w": power_watts(sta_dir / "power.rpt"),
                     "rtl_elapsed_s": rtl_time, "gls_opensta_elapsed_s": time.monotonic() - started})
    left = [(row["workload"], row["rtl_transitions_per_cycle"]) for row in rows]
    right = [(row["workload"], row["gate_power_w"]) for row in rows]
    result = {"scope": "bounded_projection", "max_blocks": args.max_blocks,
              "correlation": rank_agreement(left, right), "rows": rows}
    (args.out / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"rows": len(rows), "spearman_rho": result["correlation"]["spearman_rho"], "out": str(args.out)}))


if __name__ == "__main__":
    main()
