#!/usr/bin/env python3
"""Validate one AES workload corpus against two pre-built PDK netlists."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agcws.analysis.rank_agreement import rank_agreement
from agcws.nodes.power import parse_opensta_power_file


def _power(report: Path) -> float:
    if not report.is_file():
        raise FileNotFoundError(f"missing OpenSTA report: {report}")
    return float(parse_opensta_power_file(report).mean_power)


def validate(corpus: Path, sky_synthesis: Path, nangate_synthesis: Path,
             output: Path) -> dict:
    records = []
    for workload in sorted(corpus.glob("trial-*/workload.json")):
        trial = workload.parent.name
        sky_report = sky_synthesis / trial / "power.rpt"
        nangate_report = nangate_synthesis / trial / "power.rpt"
        records.append({
            "trial": trial,
            "workload": json.loads(workload.read_text()),
            "sky130hd": _power(sky_report),
            "nangate45": _power(nangate_report),
        })
    if not records:
        raise ValueError(f"no trial-*/workload.json files found below {corpus}")
    left = [(r["trial"], r["sky130hd"]) for r in records]
    right = [(r["trial"], r["nangate45"]) for r in records]
    result = {
        "corpus": str(corpus),
        "workloads": len(records),
        "rank_agreement": rank_agreement(left, right),
        "pdks": {
            "sky130hd": {"min_w": min(r["sky130hd"] for r in records),
                          "max_w": max(r["sky130hd"] for r in records)},
            "nangate45": {"min_w": min(r["nangate45"] for r in records),
                           "max_w": max(r["nangate45"] for r in records)},
        },
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("sky_synthesis", type=Path)
    parser.add_argument("nangate_synthesis", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.corpus, args.sky_synthesis,
                              args.nangate_synthesis, args.out), indent=2))


if __name__ == "__main__":
    main()
