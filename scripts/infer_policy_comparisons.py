#!/usr/bin/env python3
"""Run preregistered paired comparisons over run-summary directories."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.analysis.inference import (holm_bonferroni,
                                      paired_permutation_pvalue,
                                      rank_biserial_effect)

DISALLOWED_POLICY_ALIASES = {"agent", "hybrid"}


def summaries(roots: list[Path]) -> list[dict]:
    rows = []
    for root in roots:
        for path in sorted(root.rglob("summary.json")):
            row = json.loads(path.read_text())
            row["source_root"] = str(root)
            rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", type=Path, nargs="+")
    parser.add_argument("--baseline", default="random")
    parser.add_argument("--metric", choices=("auc_best_so_far", "evaluations_to_target"),
                        default="auc_best_so_far")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = summaries(args.roots)
    aliases = sorted({row.get("policy") for row in rows}
                     & DISALLOWED_POLICY_ALIASES)
    if aliases:
        parser.error("input contains ambiguous policy aliases "
                     f"{aliases}; rerun those arms with explicit policy names")
    keys = lambda row: (row.get("design"), str(row.get("target")), row.get("seed"))
    indexed = { (row.get("policy"), keys(row)): row for row in rows }
    policies = sorted({row.get("policy") for row in rows} - {args.baseline})
    comparisons = []
    for policy in policies:
        pairs = [(indexed[(args.baseline, key)], indexed[(policy, key)])
                 for key in sorted({keys(row) for row in rows})
                 if (args.baseline, key) in indexed and (policy, key) in indexed]
        if len(pairs) < 2:
            continue
        left = [float(pair[0][args.metric]) for pair in pairs]
        right = [float(pair[1][args.metric]) for pair in pairs]
        comparisons.append({"baseline": args.baseline, "policy": policy,
                            "metric": args.metric, "pairs": len(pairs),
                            "baseline_mean": sum(left) / len(left),
                            "policy_mean": sum(right) / len(right),
                            "p_value": paired_permutation_pvalue(left, right),
                            "rank_biserial": rank_biserial_effect(left, right)})
    adjusted = holm_bonferroni([row["p_value"] for row in comparisons]) if comparisons else []
    for row, value in zip(comparisons, adjusted):
        row["holm_p_value"] = value
    result = {"roots": [str(root) for root in args.roots], "comparisons": comparisons}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
