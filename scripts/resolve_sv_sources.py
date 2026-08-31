#!/usr/bin/env python3
"""Resolve a conservative SystemVerilog source closure for an OpenTitan top."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "third_party/opentitan"
ROOTS = [ROOT / "hw/ip" / name / "rtl" for name in
         ("aes", "prim", "prim_generic", "tlul", "edn", "keymgr", "lc_ctrl", "csrng", "entropy_src")]
MODULE_RE = re.compile(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)")
PACKAGE_RE = re.compile(r"\bpackage\s+([A-Za-z_][A-Za-z0-9_$]*)")
IMPORT_RE = re.compile(r"\bimport\s+([A-Za-z_][A-Za-z0-9_$]*)::")
INSTANTIATION_RE = re.compile(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_$]*)\s*(?:#\s*\([^;]*?\)\s*)?[A-Za-z_][A-Za-z0-9_$]*\s*\(")

def resolve(top: str = "aes_cipher_core", include_generated: bool = False) -> list[Path]:
    files = sorted({path for root in ROOTS for path in root.glob("*.sv")})
    files.append(ROOT / "hw/ip/prim/rtl/prim_assert.sv")
    if include_generated:
        files.append(ROOT / "hw/top_earlgrey/rtl/autogen/testing/lc_ctrl_token_pkg.sv")
    files = sorted(set(files))
    text = {path: path.read_text(errors="replace") for path in files}
    module_file = {name: path for path, body in text.items() for name in MODULE_RE.findall(body)}
    package_file = {name: path for path, body in text.items() for name in PACKAGE_RE.findall(body)}
    selected: set[Path] = set()
    pending = [top]
    while pending:
        name = pending.pop()
        path = module_file.get(name) or package_file.get(name)
        if path is None or path in selected:
            continue
        selected.add(path)
        body = text[path]
        pending.extend(IMPORT_RE.findall(body))
        # Only enqueue names found in an instantiation-shaped declaration.
        # This avoids treating arbitrary mentions/comments as dependencies.
        pending.extend(name for name in INSTANTIATION_RE.findall(body) if name in module_file)
    # Qualified references are not necessarily imports, so include the
    # package closure needed by the AES parameter/type definitions explicitly.
    for package in ("aes_reg_pkg", "prim_util_pkg", "prim_trivium_pkg", "edn_pkg", "entropy_src_pkg", "csrng_pkg", "csrng_reg_pkg"):
        if package in package_file:
            selected.add(package_file[package])
    selected.add(ROOT / "hw/ip/aes/rtl/aes_pkg.sv")
    # Verilator requires package declarations to be seen before consumers.
    packages = sorted(path for path in selected if PACKAGE_RE.search(text[path]))
    modules = sorted(selected - set(packages))
    return packages + modules

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", default="aes_cipher_core")
    parser.add_argument("--include-generated", action="store_true")
    args = parser.parse_args()
    print("\n".join(str(path) for path in resolve(args.top, args.include_generated)))
