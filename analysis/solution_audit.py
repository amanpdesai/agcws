"""Offline inspection of immutable non-flat study records; never calls an evaluator."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trials(root, cell):
    directory = root / "panel" / cell["target"] / str(cell["seed"]) / cell["arm"]
    paths = sorted(directory.glob("batches/*/trials.json.gz"))
    rows = [r for p in paths for r in read(p)]
    if [r["slot"] for r in rows] != list(range(1, 129)):
        raise ValueError("incomplete or unordered cell")
    return rows, paths


def select(root):
    manifest = read(root / "manifest.json")
    cells = read(root / "search_manifest.json")["cells"]
    selections = []
    hashes = {}
    for cell in cells:
        rows, paths = trials(root, cell)
        hashes.update({str(p.relative_to(root)): digest(p) for p in paths})
        valid = [r for r in rows if r["valid"]]
        solved = [r for r in valid if r["loss"] <= manifest["tolerance"]]
        invalid = [r for r in rows if not r["valid"]]
        roles = {
            "first_solve": solved[0]["slot"] if solved else None,
            "best": min(valid, key=lambda r: (r["loss"], r["slot"]))["slot"],
            "worst_valid": min(valid, key=lambda r: (-r["loss"], r["slot"]))["slot"],
            "first_invalid": invalid[0]["slot"] if invalid else None,
        }
        selections.append(
            {**cell, "roles": roles, "detailed": cell["seed"] == min(manifest["seeds"])}
        )
    for target in sorted({c["target"] for c in cells}):
        for arm in sorted({c["arm"] for c in cells}):
            group = [s for s in selections if s["target"] == target and s["arm"] == arm]
            first = min(group, key=lambda s: s["seed"])
            if first["roles"]["first_solve"] is None:
                solved = [s for s in group if s["roles"]["first_solve"] is not None]
                if solved:
                    min(solved, key=lambda s: s["seed"])["supplemental_first_solve"] = True
    return {
        "protocol_sha256": digest(Path("docs/SOLUTION_AUDIT.md")),
        "study_manifest_sha256": digest(root / "manifest.json"),
        "selection_basis": "slot, validity and loss only; known-outcome post-hoc inspection",
        "cells": selections,
        "trial_file_sha256": hashes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path("results/nonflat_temporal_v1"))
    parser.add_argument("--selection", type=Path, required=True)
    args = parser.parse_args()
    result = select(args.archive)
    args.selection.parent.mkdir(parents=True, exist_ok=True)
    with args.selection.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
