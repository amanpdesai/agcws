"""Small deterministic task primitives for the AGCWS experiment pipeline.

Tasks are deliberately lightweight: the expensive work remains in the EDA
tools, while this module gives each step a stable input key, manifest, and
resumable output directory.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def task_key(name: str, inputs: dict[str, Any]) -> str:
    """Return the stable key for a task name and canonical input mapping."""
    return hashlib.sha256(_canonical({"name": name, "inputs": inputs})).hexdigest()


@dataclass(frozen=True)
class TaskResult:
    name: str
    key: str
    output_dir: Path
    manifest: Path
    cached: bool


class TaskStore:
    """Filesystem-backed task store with content-addressed manifests."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        name: str,
        inputs: dict[str, Any],
        action: Callable[[Path], None],
    ) -> TaskResult:
        key = task_key(name, inputs)
        output_dir = self.root / name / key
        manifest = output_dir / "task.json"
        complete = {"name": name, "key": key, "inputs": inputs, "status": "complete"}
        if manifest.exists():
            try:
                stored = json.loads(manifest.read_text())
            except json.JSONDecodeError:
                stored = None
            if stored == complete:
                return TaskResult(name, key, output_dir, manifest, True)

        output_dir.mkdir(parents=True, exist_ok=True)
        # A crashed/interrupted action must never look resumable.  The running
        # marker is also useful when inspecting a task directory after failure.
        manifest.write_text(json.dumps(
            {"name": name, "key": key, "inputs": inputs, "status": "running"},
            indent=2,
            sort_keys=True,
        ) + "\n")
        action(output_dir)
        temporary = manifest.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(complete, indent=2, sort_keys=True) + "\n")
        temporary.replace(manifest)
        return TaskResult(name, key, output_dir, manifest, False)
