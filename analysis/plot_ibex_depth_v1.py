"""All-target mean curves and seed means, without inferred confidence bands."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis.ibex_depth_v1 import completed_prefixes, value, verify
from experiments.ibex_depth_v1.model import ARMS
from experiments.ibex_depth_v1.storage import read


def plot(root, output):
    verification = verify(root)
    manifest = read(root / "manifest.json")
    budget = max(completed_prefixes(root, manifest))
    figure, axis = plt.subplots(figsize=(10, 5))
    colors = ("#8e44ad", "#cc7722", "#24764f", "#2769aa")
    for arm, color in zip(ARMS, colors, strict=True):
        means = []
        for seed in manifest["seeds"]:
            curves = [
                value(root, f"panel/{target}/{seed}/{arm}/prefix-{budget}.json")[
                    "curve"
                ]
                for target in manifest["targets"]
            ]
            mean = [sum(column) / len(column) for column in zip(*curves, strict=True)]
            means.append(mean)
            axis.plot(
                range(1, budget + 1), mean, color=color, alpha=0.25, linewidth=0.8
            )
        axis.plot(
            range(1, budget + 1),
            [sum(c) / len(c) for c in zip(*means, strict=True)],
            color=color,
            label=arm,
            linewidth=2,
        )
    axis.axhline(
        manifest["tolerance"], linestyle=":", color="gray", label="per-run tolerance"
    )
    axis.set_xlabel("Proposed slots (includes shared initialization and failures)")
    axis.set_ylabel("Mean best-so-far normalized target error (lower is better)")
    axis.set_title(
        f"Ibex closed-loop development: {budget}-slot prefix, all four targets"
    )
    axis.grid(alpha=0.15)
    axis.legend(fontsize=8)
    state = (
        "Complete declared panel"
        if verification["complete_study"]
        else "Partial depth panel; later prefixes pending"
    )
    figure.text(
        0.5,
        0.015,
        f"{state}. Thin lines: three seed means, not confidence intervals.",
        ha="center",
        fontsize=8,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, metadata={"Date": None})
    plt.close(figure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plot(args.archive, args.out)
