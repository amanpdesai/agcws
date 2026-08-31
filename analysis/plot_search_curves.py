#!/usr/bin/env python3
"""Plot best-so-far search curves from one or more run directories."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_curves(roots: list[Path] | Path) -> dict[str, list[list[float]]]:
    groups: dict[str, list[list[float]]] = defaultdict(list)
    if isinstance(roots, Path):
        roots = [roots]
    for root in roots:
        for curve_path in sorted(root.rglob("best_so_far.json")):
            summary_path = curve_path.with_name("summary.json")
            if not summary_path.is_file():
                continue
            summary = json.loads(summary_path.read_text())
            curve = json.loads(curve_path.read_text()).get("error")
            if not isinstance(curve, list) or not curve:
                continue
            policy = str(summary.get("policy", "unknown"))
            groups[policy].append([float(value) for value in curve])
    if not groups:
        raise ValueError(f"no search curves found below {', '.join(map(str, roots))}")
    return dict(sorted(groups.items()))


def mean_curves(curves: dict[str, list[list[float]]]) -> dict[str, list[float]]:
    result = {}
    for policy, runs in curves.items():
        length = max(len(run) for run in runs)
        padded = [run + [run[-1]] * (length - len(run)) for run in runs]
        result[policy] = [sum(run[index] for run in padded) / len(padded)
                          for index in range(length)]
    return result


def plot(curves: dict[str, list[list[float]]], output: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    means = mean_curves(curves)
    figure, axis = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for policy, curve in means.items():
        axis.plot(range(1, len(curve) + 1), curve, label=policy)
    axis.set(xlabel="Proposal index", ylabel="Best-so-far target error",
             title="Search convergence")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.savefig(output, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    curves = load_curves(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plot(curves, args.out)
    summary = {"policies": {policy: {"runs": len(runs), "evaluations": max(map(len, runs))}
                             for policy, runs in curves.items()}}
    args.out.with_suffix(".json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"figure": str(args.out), "summary": str(args.out.with_suffix('.json'))},
                     sort_keys=True))


if __name__ == "__main__":
    main()
