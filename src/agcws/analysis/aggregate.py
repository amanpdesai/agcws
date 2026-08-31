"""Aggregate proposal-counted run summaries without external statistics packages."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def aggregate_summaries(records: Iterable[dict]) -> list[dict]:
    """Aggregate run summaries by policy and design.

    Every input record is retained in the denominator, including right-censored
    unsolved runs. Records may include ``policy`` and ``design`` metadata; an
    absent design is grouped as ``unknown``.
    """
    groups: defaultdict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        groups[(str(record.get("policy", "unknown")),
                str(record.get("design", "unknown")))].append(record)
    output = []
    for (policy, design), values in sorted(groups.items()):
        count = len(values)
        output.append({
            "policy": policy,
            "design": design,
            "runs": count,
            "solve_rate": sum(bool(value.get("solved", False)) for value in values) / count,
            "mean_auc_best_so_far": sum(float(value["auc_best_so_far"])
                                         for value in values) / count,
            "mean_evaluations_to_target": sum(float(value["evaluations_to_target"])
                                               for value in values) / count,
        })
    return output
