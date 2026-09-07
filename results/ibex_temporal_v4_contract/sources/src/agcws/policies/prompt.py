"""Frozen prompt loading and hashing for auditable agent experiments."""
from __future__ import annotations

import hashlib
from pathlib import Path


def prompt_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_prompt(path: Path) -> tuple[str, str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    content = path.read_text()
    if not content.strip():
        raise ValueError("frozen prompt is empty")
    return content, prompt_hash(path)
