#!/usr/bin/env python3
"""Run the pinned Slang/Yosys Ibex elaboration probe and capture diagnostics."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def resolve_source_path(value: str, repository_root: Path) -> Path:
    """Resolve container-rooted FuseSoC paths against the local checkout."""
    path = Path(value)
    if path.is_file():
        return path
    if value.startswith("/workspace/"):
        candidate = repository_root / value.removeprefix("/workspace/")
        if candidate.is_file():
            return candidate
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path, default=Path("out/ibex-sources-top/sources.json"), nargs="?")
    parser.add_argument("--out", type=Path, default=Path("out/ibex-synthesis-probe"))
    parser.add_argument("--top", default="ibex_top")
    args = parser.parse_args()
    manifest = json.loads(args.sources.read_text())
    repository_root = Path(__file__).resolve().parents[1]
    original_paths = [str(item["path"]) for item in manifest["sources"]]
    source_paths = [str(resolve_source_path(path, repository_root))
                    for path in original_paths]
    include_dir_paths = {Path(path).parent for path in source_paths}
    # FuseSoC's generated source list does not always carry include-only files.
    include_dir_paths.update({
        repository_root / "third_party/ibex/vendor/lowrisc_ip/ip/prim/rtl",
        repository_root / "third_party/ibex/vendor/lowrisc_ip/dv/sv/dv_utils",
        repository_root / "third_party/ibex/build/lowrisc_ibex_ibex_top_0.1/lint-verilator/src/lowrisc_prim_util_memload_0/rtl",
    })
    for filename in ("prim_util_memload.svh", "dv_fcov_macros.svh"):
        include_dir_paths.update(path.parent for path in
                                 (repository_root / "third_party/ibex").rglob(filename))
    if any("third_party/ibex" in path for path in source_paths):
        secded = repository_root / "third_party/ibex/vendor/lowrisc_ip/ip/prim/rtl/prim_secded_pkg.sv"
        if secded.is_file():
            source_paths.append(str(secded))
            include_dir_paths.add(secded.parent)
    include_dirs = sorted(str(path) for path in include_dir_paths if path.is_dir())
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
        "source_count": len(source_paths), "original_source_paths": original_paths,
        "resolved_source_paths": source_paths, "command": [yosys, "-Q", "-p", read],
        "returncode": result.returncode,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "returncode": result.returncode,
                      "sources": len(source_paths)}, sort_keys=True))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
