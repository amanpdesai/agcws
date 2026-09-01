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


def verify_activity(root: Path, *, required: bool = False) -> None:
    """Validate the structural invariants of a persisted activity artifact."""
    activity_path = root / "activity.json"
    if not activity_path.is_file():
        if required:
            raise FileNotFoundError(f"missing activity artifact: {activity_path}")
        return
    activity = json.loads(activity_path.read_text())
    cycles = activity.get("per_cycle_toggles")
    windows = activity.get("window_toggles")
    normalized = activity.get("normalized_windows")
    if not isinstance(cycles, list) or not isinstance(windows, list):
        return  # legacy non-AES artifacts may carry a minimal activity record
    if isinstance(normalized, list):
        if len(normalized) != len(windows):
            raise ValueError("activity normalized profile does not match windows")
        if any(float(value) < 0 for value in cycles + windows):
            raise ValueError("activity toggle counts cannot be negative")
        peak = max(windows, default=0)
        expected = [0.0 for _ in windows] if peak == 0 else [float(v) / peak for v in windows]
        if normalized != expected:
            raise ValueError("activity normalized profile is inconsistent with windows")
    # Pre-normalization AES artifacts remain structurally verifiable; continue
    # to the waveform digest check when the legacy record includes one.
    digest = activity.get("waveform_sha256")
    if digest is None:
        return
    waveform = root / str(activity.get("vcd", "activity.vcd"))
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("activity has no valid waveform SHA-256")
    if waveform.is_file() and sha256(waveform) != digest:
        raise ValueError("activity waveform SHA-256 mismatch")


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

    verify_activity(root)

    return {"artifact": str(root), "valid": True, "inputs_checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--require-activity", action="store_true")
    args = parser.parse_args()
    result = verify(args.artifact)
    verify_activity(args.artifact, required=args.require_activity)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
