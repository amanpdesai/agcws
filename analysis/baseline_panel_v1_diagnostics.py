"""Post-hoc algebraic target difficulty, never a change to frozen selection."""

import argparse
import statistics
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_depth_v1.storage import ensure, read


def flat_error(rates, scale):
    return statistics.pstdev(rates) / scale


def diagnose(archive):
    manifest = read(archive / "manifest.json")
    targets = read(archive / "targets.json")
    return {
        "status": "post-hoc diagnostic, not predeclared target selection",
        "target_sha256": file_sha256(archive / "targets.json"),
        "summary_sha256": file_sha256(archive / "summary.json"),
        "scope": "best constant vector is algebraic, not a witnessed legal workload",
        "targets": [
            {
                "target": t["id"],
                "best_constant_rate": statistics.mean(t["target_rates"]),
                "best_constant_nrmse": flat_error(t["target_rates"], manifest["scale"]),
                "constant_vector_within_tolerance": flat_error(
                    t["target_rates"], manifest["scale"]
                )
                <= manifest["tolerance"],
                "normalized_range": (max(t["target_rates"]) - min(t["target_rates"]))
                / manifest["scale"],
            }
            for t in targets
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--archive", type=Path, default=Path("results/baseline_panel_v1")
    )
    args = parser.parse_args()
    result = diagnose(args.archive)
    ensure(args.archive / "difficulty_diagnostic.json", result)
    print(result)
