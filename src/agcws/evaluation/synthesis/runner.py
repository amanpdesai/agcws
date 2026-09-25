"""Mapped-netlist artifact shared by the power runner and CHIA bindings."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NetlistArtifact:
    netlist: Path
    liberty: Path
    manifest: Path
