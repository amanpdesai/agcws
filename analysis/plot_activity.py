#!/usr/bin/env python3
"""Plot recorded AES activity without rerunning simulation or STA."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def summarize(activity: dict) -> dict:
    cycles = [int(value) for value in activity.get("per_cycle_toggles", [])]
    windows = [int(value) for value in activity.get("window_toggles", [])]
    if not cycles:
        raise ValueError("activity has no per_cycle_toggles")
    return {
        "clock_edges": int(activity.get("clock_edges", len(cycles))),
        "total_transitions": int(activity.get("total_transitions", sum(cycles))),
        "per_cycle_mean": sum(cycles) / len(cycles),
        "per_cycle_peak": max(cycles),
        "window_count": len(windows),
        "window_toggles": windows,
        "window_normalized": [value / max(windows) for value in windows] if windows and max(windows) else [],
    }


def plot(activity: dict, output: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if "per_cycle_toggles" not in activity:
        raise ValueError(
            "activity artifact has no per_cycle_toggles; rerun the evaluator "
            "with cycle-level activity enabled"
        )
    cycles = [int(value) for value in activity["per_cycle_toggles"]]
    windows = [int(value) for value in activity.get("window_toggles", [])]
    figure, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    axes[0].plot(range(len(cycles)), cycles, linewidth=0.8)
    axes[0].set(title="Per-cycle RTL switching activity", xlabel="Clock cycle", ylabel="Bit transitions")
    axes[0].grid(alpha=0.25)
    axes[1].bar(range(len(windows)), windows)
    axes[1].set(title="Coarse-window switching activity", xlabel="Window", ylabel="Bit transitions")
    axes[1].grid(axis="y", alpha=0.25)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("activity", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="PNG output path")
    args = parser.parse_args()
    activity = json.loads(args.activity.read_text())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plot(activity, args.out)
    summary_path = args.out.with_suffix(".json")
    summary_path.write_text(json.dumps(summarize(activity), indent=2) + "\n")
    print(json.dumps({"figure": str(args.out), "summary": str(summary_path)}, indent=2))


if __name__ == "__main__":
    main()
