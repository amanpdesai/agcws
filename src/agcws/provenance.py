"""Portable provenance records for experiment artifacts."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command_version(command: str | Path, *args: str) -> str | None:
    try:
        result = subprocess.run([str(command), *args], capture_output=True,
                                text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return (result.stdout or result.stderr).strip().splitlines()[0] if (result.stdout or result.stderr).strip() else ""


def toolchain_record(commands: dict[str, str | Path]) -> dict[str, str | None]:
    return {name: command_version(command, "--version") for name, command in commands.items()}


def input_record(paths: dict[str, Path]) -> dict[str, dict[str, str | int]]:
    return {
        name: {"path": str(path), "bytes": path.stat().st_size, "sha256": file_sha256(path)}
        for name, path in paths.items()
    }
