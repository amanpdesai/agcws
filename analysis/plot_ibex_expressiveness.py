"""Show every development seed's finalist; no selected winning examples."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis.ibex_expressiveness import verify


def plot(root, output):
    verify(root)
    manifest = json.loads((root / "manifest.json").read_text())
    targets, policies = list(manifest["targets"]), manifest["policies"]
    figure, axes = plt.subplots(
        len(targets), len(policies), figsize=(11, 9), sharex=True, sharey=True
    )
    colors = ["#1976b8", "#dc7c22", "#32946a"]
    for row, target in enumerate(targets):
        for col, policy in enumerate(policies):
            axis = axes[row, col]
            axis.step(
                range(1, 9),
                manifest["targets"][target]["rates"],
                where="mid",
                color="black",
                linestyle="--",
                label="target",
            )
            for seed, color in zip(manifest["seeds"], colors):
                path = (
                    root / "panel" / target / f"seed-{seed}" / policy / "trials.jsonl"
                )
                trials = [json.loads(line) for line in path.read_text().splitlines()]
                valid = [t for t in trials if t["valid"]]
                if valid:
                    best = min(valid, key=lambda t: t["loss"])
                    axis.step(
                        range(1, 9),
                        best["rates"],
                        where="mid",
                        color=color,
                        alpha=0.75,
                        label=str(seed),
                    )
            axis.set_title(f"{target} / {policy}", fontsize=10)
            axis.grid(alpha=0.15)
            axis.set_xticks(range(1, 9))
    axes[0, 0].legend(title="development seed", fontsize=7)
    figure.supxlabel("Equal-duration measurement bin")
    figure.supylabel("Core bit transitions per clock edge (not watts)")
    figure.suptitle(
        "Ibex development: all 36 within-budget finalists; no held-out claim"
    )
    figure.tight_layout(rect=[0.02, 0.02, 1, 0.97])
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, metadata={"Date": None})
    plt.close(figure)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plot(args.archive, args.out)
