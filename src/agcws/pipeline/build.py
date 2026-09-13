"""Serialize shared simulator builds and publish only verified completions."""

import fcntl
import json
from pathlib import Path

from agcws.provenance import file_sha256


def ensure_binary(directory: Path, name: str, compile_binary):
    directory.mkdir(parents=True, exist_ok=True)
    if Path(name).name != name or name in ("", ".", ".."):
        raise ValueError("binary name must be a single filename")
    binary = directory / name
    stamp = directory / f"{name}.complete.json"
    with (directory / f"{name}.build.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if stamp.exists():
            recorded = json.loads(stamp.read_text())
            if not binary.is_file() or file_sha256(binary) != recorded["sha256"]:
                raise ValueError("completed simulator cache was modified")
            return binary
        # A binary without a completion stamp may belong to an interrupted build.
        compile_binary(binary)
        if not binary.is_file() or not binary.stat().st_mode & 0o111:
            raise ValueError("compiler did not produce an executable simulator")
        pending = directory / f"{name}.complete.pending"
        pending.write_text(json.dumps({"sha256": file_sha256(binary)}) + "\n")
        pending.replace(stamp)
    return binary
