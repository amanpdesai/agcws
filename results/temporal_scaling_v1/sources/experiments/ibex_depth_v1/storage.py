"""Atomic immutable checkpoints; interrupted requests are never resampled."""

import json
import os
import tempfile
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, allow_nan=False) + "\n"
    descriptor, name = tempfile.mkstemp(prefix=".checkpoint-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(name, path)
    finally:
        os.unlink(name)


def ensure(path, value):
    if path.exists():
        if read(path) != value:
            raise ValueError(f"checkpoint differs: {path}")
    else:
        write(path, value)
