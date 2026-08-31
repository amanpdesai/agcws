#!/usr/bin/env python3
"""Emit the OpenTitan AES RTL source set for harness/synthesis commands."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "third_party/opentitan"

def sources() -> list[Path]:
    # aes.core declares the IP files; dependencies are added as the harness
    # reaches them. Keeping this explicit makes source provenance inspectable.
    aes = ROOT / "hw/ip/aes/rtl"
    return sorted(aes.glob("*.sv"))

if __name__ == "__main__":
    print("\n".join(str(path) for path in sources()))
