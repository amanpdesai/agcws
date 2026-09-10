"""Post-hoc constant-vector floor and observed solves; no endpoint changes."""

import argparse
import statistics
from pathlib import Path

from agcws.provenance import file_sha256
from analysis.baseline_panel_v1_diagnostics import flat_error
from analysis.ibex_depth_v1 import value
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.storage import ensure, read


def diagnose(root):
    manifest = read(root / "manifest.json")
    rows = []
    for name, target in manifest["targets"].items():
        floor = flat_error(target["rates"], manifest["scale"])
        solves = {}
        for arm in manifest["arms"]:
            solves[arm] = 0
            for seed in manifest["seeds"]:
                history = [
                    t
                    for offset in range(1, 129, 2)
                    for t in value(
                        root,
                        f"panel/{name}/{seed}/{arm}/batches/{offset:03}/trials.json",
                    )
                ]
                solves[arm] += summarize(history, 128, manifest["tolerance"])["solved"]
        rows.append(
            {
                "target": name,
                "best_constant_rate": statistics.mean(target["rates"]),
                "constant_floor": floor,
                "requires_nonconstant": floor > manifest["tolerance"],
                "solves_by_arm": solves,
            }
        )
    return {
        "status": "post-hoc algebraic diagnostic; original endpoints unchanged",
        "manifest_sha256": file_sha256(root / "manifest.json"),
        "aggregate_sha256": file_sha256(root / "aggregate.json"),
        "scope": "A constant vector is not necessarily a realizable legal workload.",
        "targets": rows,
        "nonconstant_required_solves": {
            arm: sum(r["solves_by_arm"][arm] for r in rows if r["requires_nonconstant"])
            for arm in manifest["arms"]
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("results/ibex_depth_v1"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/ibex_depth_flat_diagnostic_v1/summary.json"),
    )
    args = parser.parse_args()
    result = diagnose(args.root)
    ensure(args.output, result)
    print(result)
