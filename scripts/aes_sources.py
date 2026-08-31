#!/usr/bin/env python3
"""Emit the OpenTitan AES RTL source set for harness/synthesis commands."""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1] / "third_party/opentitan"

def sources(include_generated: bool = True) -> list[Path]:
    """Return a transparent first-pass source set for an AES compile probe."""
    roots = [ROOT / f"hw/ip/{name}/rtl" for name in
             ("aes", "prim", "prim_generic", "tlul", "edn", "keymgr", "lc_ctrl")]
    paths = [path for root in roots for path in root.glob("*.sv")]
    excluded = {"prim_racl_error_arb.sv", "tlul_adapter_shim.sv", "tlul_adapter_vh.sv"}
    paths = [path for path in paths if path.name not in excluded]
    if include_generated:
        paths.append(ROOT / "hw/top_earlgrey/rtl/autogen/testing/lc_ctrl_token_pkg.sv")
    return sorted(set(paths))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-generated", action="store_true")
    args = parser.parse_args()
    print("\n".join(str(path) for path in sources(not args.no_generated)))
