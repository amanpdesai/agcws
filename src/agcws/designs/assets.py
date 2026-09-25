"""Resolve installed first-party harness assets independently of the workspace."""

from pathlib import Path


def asset_path(design: str, name: str) -> Path:
    if design not in {"aes", "dma", "ibex", "mesh", "redmule"}:
        raise ValueError("unknown design asset owner")
    if not name or Path(name).name != name or name in {".", ".."}:
        raise ValueError("asset name must be a single path component")
    path = Path(__file__).resolve().parent / design / "assets" / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path
