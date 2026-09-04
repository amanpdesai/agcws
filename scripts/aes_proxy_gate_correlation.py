#!/usr/bin/env python3
"""Compare RTL activity and GLS/OpenSTA on bounded AES workload projections."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def dynamic_power(report: Path) -> float:
    text = report.read_text()
    match = re.search(r"^Total\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"OpenSTA dynamic power not found in {report}")
    return float(match.group(1)) + float(match.group(2))


def partial_spearman(rows: list[dict]) -> float:
    blocks = sorted({row["projected_blocks"] for row in rows})
    def residuals(key: str) -> list[float]:
        values = [row[key] for row in rows]
        means = {block: sum(row[key] for row in rows if row["projected_blocks"] == block) /
                 sum(row["projected_blocks"] == block for row in rows) for block in blocks}
        return [value - means[row["projected_blocks"]] for value, row in zip(values, rows)]
    x, y = residuals("rtl_rate"), residuals("gate_dynamic_power_w")
    mx, my = sum(x) / len(x), sum(y) / len(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denominator = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("synthesis", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ladder", type=int, nargs="+", default=[1, 2, 4, 8, 16, 32])
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
        original = json.loads(source.read_text())
        for blocks in args.ladder:
            workload = project(original, blocks)
            tag = f"workload-{index:03d}-blocks-{blocks}"
            item_dir = args.out / tag
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
            environment = dict(os.environ)
            environment["AGCWS_VCD_SCOPE"] = "aes_core_gls/dut"
            subprocess.run(["bash", "scripts/run_opensta_aes.sh", str(args.synthesis), str(gls_dir / "activity.vcd"), str(sta_dir)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, env=environment)
            gls = json.loads((gls_dir / "activity.json").read_text())
            rows.append({"workload": source.name, "projected_blocks": blocks,
                         "rtl_rate": rtl["total_transitions"] / rtl["clock_edges"],
                         "gls_rate": gls["total_transitions"] / gls["clock_edges"],
                         "gls_clock_edges": gls["clock_edges"],
                         "rtl_total_transitions": rtl["total_transitions"],
                         "rtl_clock_edges": rtl["clock_edges"],
                         "gate_dynamic_power_w": dynamic_power(sta_dir / "power.rpt"),
                         "rtl_elapsed_s": rtl_time, "gls_opensta_elapsed_s": time.monotonic() - started})
    for row in rows:
        row["gls_dynamic_energy_j"] = row["gate_dynamic_power_w"] * row["gls_clock_edges"] * 10e-9
    pooled_left = [(f'{row["workload"]}@{row["projected_blocks"]}', row["rtl_rate"]) for row in rows]
    pooled_right = [(f'{row["workload"]}@{row["projected_blocks"]}', row["gate_dynamic_power_w"]) for row in rows]
    correlations = {"pooled": rank_agreement(pooled_left, pooled_right), "per_rung": []}
    for blocks in args.ladder:
        subset = [row for row in rows if row["projected_blocks"] == blocks]
        left = [(row["workload"], row["rtl_rate"]) for row in subset]
        right = [(row["workload"], row["gate_dynamic_power_w"]) for row in subset]
        correlations["per_rung"].append({"projected_blocks": blocks, "correlation": rank_agreement(left, right)})
    correlations["partial_spearman_by_block_mean"] = partial_spearman(rows)
    result = {"scope": "block_count_ladder_projection", "ladder": args.ladder,
              "power_metric": "opensta_internal_plus_switching_w", "correlations": correlations, "rows": rows}
    (args.out / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"rows": len(rows), "correlations": correlations, "out": str(args.out)}))


if __name__ == "__main__":
    main()
