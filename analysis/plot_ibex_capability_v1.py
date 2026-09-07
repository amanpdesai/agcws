"""Show every fixed-context gain, preserving target heterogeneity."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis.ibex_capability_v1 import verify
from experiments.ibex_capability_v1.study import ARMS, read


def plot(root, output):
    verify(root)
    manifest = read(root / "manifest.json")
    aggregate = read(root / "aggregate.json")
    targets = sorted({c["target"] for c in manifest["contexts"].values()})
    colors = ("#2563a6", "#d97706", "#24834b", "#9749a0")
    figure, axis = plt.subplots(figsize=(10, 5))
    for x, arm in enumerate(ARMS):
        for i, target in enumerate(targets):
            contexts = [
                name
                for name, c in manifest["contexts"].items()
                if c["target"] == target
            ]
            gains = [
                read(root / "cells" / c / arm / "result.json")["summary"]["gain"]
                for c in contexts
            ]
            axis.scatter(
                [x + (i - 1.5) * 0.13] * len(gains),
                gains,
                color=colors[i],
                alpha=0.75,
                s=35,
                label=target if x == 0 else None,
            )
        axis.plot(
            x,
            aggregate["arms"][arm]["mean_gain"],
            marker="_",
            markersize=25,
            color="black",
            markeredgewidth=2,
            label="all-context mean" if x == 0 else None,
        )
    axis.axhline(0, color="grey", linewidth=0.7)
    axis.set_xticks(range(len(ARMS)), ARMS)
    axis.set_ylabel("Reduction in normalized target error (higher is better)")
    axis.set_title(
        "Ibex capability probe: all 12 contexts per arm, two proposed programs each"
    )
    axis.grid(axis="y", alpha=0.15)
    axis.legend(fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    figure.text(
        0.5,
        0.01,
        "Observed development histories; three reused seeds. Not on-policy AUC or held-out inference.",
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
