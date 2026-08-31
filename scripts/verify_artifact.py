#!/usr/bin/env python3
"""Verify hashes and required fields in one AGCWS evaluation artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(root: Path) -> dict:
    result_path = root / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"missing result.json: {result_path}")
    result = json.loads(result_path.read_text())
    if not result.get("valid"):
        raise ValueError("artifact result is not valid")
    if result.get("useful_work", 0) <= 0:
        raise ValueError("artifact does not report useful work")

    provenance = result.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("result has no provenance object")
    inputs = provenance.get("inputs")
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError("provenance has no input records")

    checked = 0
    for name, record in inputs.items():
        if not isinstance(record, dict) or not record.get("path") or not record.get("sha256"):
            raise ValueError(f"invalid provenance input record: {name}")
        path = Path(record["path"])
        if not path.is_absolute():
            # Prefer the artifact directory for portable bundles, then the
            # current repository for records referring to shared inputs.
            local_path = root / path
            path = local_path if local_path.is_file() else Path.cwd() / path
        if not path.is_file():
            raise FileNotFoundError(f"missing input for {name}: {path}")
        actual = sha256(path)
        if actual != record["sha256"]:
            raise ValueError(f"sha256 mismatch for {name}: {actual} != {record['sha256']}")
        if "bytes" in record and path.stat().st_size != record["bytes"]:
            raise ValueError(f"byte-count mismatch for {name}")
        checked += 1

    return {"artifact": str(root), "valid": True, "inputs_checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.artifact), sort_keys=True))


if __name__ == "__main__":
    main()
