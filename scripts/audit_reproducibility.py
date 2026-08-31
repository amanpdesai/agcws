#!/usr/bin/env python3
"""Check repository inputs required for a reproducible AGCWS run."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


REQUIRED = (
    ".env.example",
    ".gitmodules",
    "LICENSE",
    "prompts/agent_system_v1.txt",
    "third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib",
    "third_party/liberty/nangate45/Nangate45_typ.lib",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root: Path) -> dict:
    missing = [path for path in REQUIRED if not (root / path).is_file()
               or (root / path).stat().st_size == 0]
    submodule = root / "tools" / "chia"
    try:
        commit = subprocess.run(
            ["git", "-C", str(submodule), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = None
    prompt = root / "prompts" / "agent_system_v1.txt"
    return {
        "valid": not missing and commit is not None,
        "missing": missing,
        "chia_commit": commit,
        "inputs": {
            path: {"bytes": (root / path).stat().st_size,
                   "sha256": digest(root / path)}
            for path in REQUIRED if path not in missing
        },
        "prompt_sha256": digest(prompt) if prompt.is_file() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = audit(args.root.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
