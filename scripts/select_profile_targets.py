#!/usr/bin/env python3
"""Select deterministic held-out, achieved AES profiles as experiment goals."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def select(corpus: Path, kind: str, *, seed: int = 0, holdout: float = 0.25) -> list[dict]:
    records = [json.loads(line) for line in corpus.read_text().splitlines() if line.strip()]
    if not records:
        raise ValueError("profile corpus is empty")
    if not 0 < holdout < 1:
        raise ValueError("holdout must be between zero and one")
    field = "normalized_windows" if kind == "temporal" else "by_region"
    eligible = [record for record in records if record.get(field)]
    if not eligible:
        raise ValueError(f"corpus contains no {kind} profiles")
    order = list(range(len(eligible)))
    random.Random(seed).shuffle(order)
    count = max(1, round(len(order) * holdout))
    selected = []
    for position in order[:count]:
        record = eligible[position]
        if kind == "temporal":
            profile = record["normalized_windows"]
            selected.append({"source": record.get("name", position),
                             "windows": len(profile), "profile": profile})
        else:
            values = record["by_region"]
            total = sum(float(value) for value in values.values())
            if total <= 0:
                continue
            selected.append({"source": record.get("index", position),
                             "shares": {key: float(value) / total
                                        for key, value in values.items()
                                        if key != "unattributed"}})
    if not selected:
        raise ValueError("selected profiles have no positive activity")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("kind", choices=("temporal", "compositional"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--holdout", type=float, default=0.25)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = {"kind": args.kind, "seed": args.seed,
               "holdout": args.holdout,
               "targets": select(args.corpus, args.kind, seed=args.seed,
                                 holdout=args.holdout)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
