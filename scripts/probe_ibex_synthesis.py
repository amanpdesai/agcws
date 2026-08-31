#!/usr/bin/env python3
"""Run the pinned Slang/Yosys Ibex elaboration probe and capture diagnostics."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path, default=Path("out/ibex-sources-top/sources.json"), nargs="?")
    parser.add_argument("--out", type=Path, default=Path("out/ibex-synthesis-probe"))
    parser.add_argument("--top", default="ibex_top")
    args = parser.parse_args()
    manifest = json.loads(args.sources.read_text())
    source_paths = [str(item["path"]) for item in manifest["sources"]]
    include_dirs = sorted({str(Path(path).parent) for path in source_paths})
    yosys = os.environ.get("AGCWS_YOSYS", "yosys")
    plugin = os.environ.get("AGCWS_SLANG_PLUGIN", "")
    if not plugin:
        raise SystemExit("AGCWS_SLANG_PLUGIN is required for the Ibex probe")
    read = (f"plugin -i {plugin}; read_slang --top {args.top} -D SYNTHESIS "
            + " ".join(f"-I {path}" for path in include_dirs)
            + " " + " ".join(source_paths))
    args.out.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([yosys, "-Q", "-p", read], capture_output=True, text=True)
    (args.out / "yosys.log").write_text("STDOUT\n" + result.stdout + "\nSTDERR\n" + result.stderr)
    (args.out / "manifest.json").write_text(json.dumps({
        "top": args.top, "sources": args.sources.resolve().as_posix(),
        "source_count": len(source_paths), "command": [yosys, "-Q", "-p", read],
        "returncode": result.returncode,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "returncode": result.returncode,
                      "sources": len(source_paths)}, sort_keys=True))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
