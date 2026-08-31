#!/usr/bin/env python3
"""Lint the resolved Ibex RTL closure with the production Verilator tool."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path)
    parser.add_argument("--top", default="ibex_top")
    args = parser.parse_args()
    manifest = json.loads(args.sources.read_text())
    root = Path(__file__).resolve().parents[1] / "third_party" / "ibex"
    include_dirs = {Path(item["path"]).parent for item in manifest["sources"]}
    for filename in ("prim_util_memload.svh", "dv_fcov_macros.svh"):
        include_dirs.update(path.parent for path in root.rglob(filename))
    command = [os.environ.get("AGCWS_VERILATOR", "verilator"), "--lint-only",
               "--language", "1800-2012", "--top-module", args.top,
               "-DSYNTHESIS", "-Wno-fatal"]
    command += [f"-I{path}" for path in sorted(include_dirs)]
    command += [str(item["path"]) for item in manifest["sources"]]
    result = subprocess.run(command, text=True)
    print(json.dumps({"sources": len(manifest["sources"]),
                      "returncode": result.returncode}, sort_keys=True))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
