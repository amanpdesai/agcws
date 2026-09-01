#!/usr/bin/env python3
"""Validate generated memory collateral without running synthesis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def audit(directory: Path) -> dict:
    manifest = json.loads((directory / "memory-macros.json").read_text())
    config = json.loads((directory / "bsg_fakeram.json").read_text())
    macros = manifest["macros"]
    errors = []
    if len(config.get("srams", [])) != len(macros):
        errors.append("BSG config count differs from macro manifest")
    for macro, sram in zip(macros, config.get("srams", []), strict=False):
        expected = f"fakeram{config['tech_nm']}_{macro['physical_depth']}x{macro['physical_width']}"
        if sram.get("name") != expected:
            errors.append(f"{macro['source_name']}: BSG name does not match physical geometry")
        if sram.get("width") != macro["physical_width"]:
            errors.append(f"{macro['source_name']}: physical width mismatch")
        if sram.get("depth") != macro["physical_depth"]:
            errors.append(f"{macro['source_name']}: physical depth mismatch")
    expected_ready = all(macro["mapping_eligible"] for macro in macros)
    if manifest["mapping_ready"] != expected_ready:
        errors.append("mapping_ready disagrees with per-macro eligibility")
    result = {"directory": str(directory), "macros": len(macros),
              "mapping_ready": manifest["mapping_ready"], "errors": errors,
              "valid": not errors}
    if errors:
        raise ValueError(json.dumps(result, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.directory), sort_keys=True))


if __name__ == "__main__":
    main()
