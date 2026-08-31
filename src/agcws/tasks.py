"""Small deterministic task primitives for the AGCWS experiment pipeline.

Tasks are deliberately lightweight: the expensive work remains in the EDA
tools, while this module gives each step a stable input key, manifest, and
resumable output directory.
"""
from __future__ import annotations

from dataclasses import dataclass
import fcntl
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
        *,
        required_outputs: tuple[str, ...] = (),
    ) -> TaskResult:
        key = task_key(name, inputs)
        output_dir = self.root / name / key
        manifest = output_dir / "task.json"
        for relative in required_outputs:
            output_path = Path(relative)
            if output_path.is_absolute() or ".." in output_path.parts:
                raise ValueError(f"required output must stay inside task directory: {relative}")
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / ".lock").open("w") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            complete = {"name": name, "key": key, "inputs": inputs, "status": "complete"}
            if manifest.exists():
                try:
                    stored = json.loads(manifest.read_text())
                except json.JSONDecodeError:
                    stored = None
                outputs_exist = all((output_dir / relative).is_file()
                                    for relative in required_outputs)
                if stored == complete and outputs_exist:
                    return TaskResult(name, key, output_dir, manifest, True)

            # A crashed/interrupted action must never look resumable.
            manifest.write_text(json.dumps(
                {"name": name, "key": key, "inputs": inputs, "status": "running"},
                indent=2, sort_keys=True,
            ) + "\n")
            try:
                action(output_dir)
            except Exception as exc:
                manifest.write_text(json.dumps({
                    "name": name, "key": key, "inputs": inputs,
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                }, indent=2, sort_keys=True) + "\n")
                raise
            missing = [relative for relative in required_outputs
                       if not (output_dir / relative).is_file()]
            if missing:
                error = f"task did not produce required outputs: {', '.join(missing)}"
                manifest.write_text(json.dumps({
                    "name": name, "key": key, "inputs": inputs,
                    "status": "failed", "error": error,
                }, indent=2, sort_keys=True) + "\n")
                raise FileNotFoundError(error)
            temporary = manifest.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(complete, indent=2, sort_keys=True) + "\n")
            temporary.replace(manifest)
            return TaskResult(name, key, output_dir, manifest, False)
