#!/usr/bin/env python3
"""Run the pinned Slang/Yosys Ibex elaboration probe and capture diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    parser.add_argument("--map", action="store_true",
                        help="continue through Yosys mapping and write mapped.v")
    parser.add_argument("--liberty", type=Path,
                        default=Path(os.environ.get("AGCWS_LIBERTY",
                            "third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib")))
    args = parser.parse_args()
    manifest = json.loads(args.sources.read_text())
    repository_root = Path(__file__).resolve().parents[1]
    original_paths = [str(item["path"]) for item in manifest["sources"]]
    source_paths = [str(resolve_source_path(path, repository_root))
                    for path in original_paths]
    include_dir_paths = {Path(path).parent for path in source_paths}
    # FuseSoC's generated source list does not always carry include-only files.
    # Keep the shared primitive include roots, but only add generated include
    # directories that belong to the resolved closure.  Searching the whole
    # checkout here can pull simple-system-only memload headers into an
    # ibex_core probe and make Slang parse them at compilation-unit scope.
    include_dir_paths.update({
        repository_root / "third_party/ibex/vendor/lowrisc_ip/ip/prim/rtl",
        repository_root / "third_party/ibex/vendor/lowrisc_ip/dv/sv/dv_utils",
    })
    for filename in ("prim_util_memload.svh", "dv_fcov_macros.svh"):
        include_dir_paths.update(
            path.parent for path in
            (Path(path).parent for path in source_paths)
            if (path / filename).is_file()
        )
    # FuseSoC may preserve include-only directories from another target in its
    # generated manifest.  They are unsafe for a core-only probe unless the
    # resolved source closure actually contains that header.
    if args.top == "ibex_core":
        include_dir_paths = {
            path for path in include_dir_paths
            if "prim_util_memload" not in str(path)
            and "simple_system" not in str(path)
        }
    if any("third_party/ibex" in path for path in source_paths):
        package_root = repository_root / "third_party/ibex/vendor/lowrisc_ip/ip/prim/rtl"
        # The resolver may include both the original vendor copy and FuseSoC's
        # exported copy.  Slang rejects duplicate package declarations; retain
        # the exported closure whenever it exists.
        package_names = {"prim_secded_pkg.sv", "prim_util_pkg.sv",
                         "prim_cipher_pkg.sv", "prim_count.sv", "prim_count_pkg.sv"}
        for package in package_names:
            paths = [path for path in source_paths if Path(path).name == package]
            if len(paths) > 1 and any("fusesoc-work" in path for path in paths):
                source_paths = [
                    path for path in source_paths
                    if not (Path(path).name == package
                            and "third_party/ibex/vendor" in path)
                ]
        # insert(0) reverses this sequence; keep packages before consumers.
        existing_names = {Path(path).name for path in source_paths}
        for package in ("prim_secded_pkg.sv", "prim_util_pkg.sv", "prim_cipher_pkg.sv",
                        "prim_count.sv", "prim_count_pkg.sv"):
            path = package_root / package
            if path.is_file() and package not in existing_names:
                source_paths.insert(0, str(path))
                include_dir_paths.add(path.parent)
    include_dirs = sorted(str(path) for path in include_dir_paths if path.is_dir())
    yosys = os.environ.get("AGCWS_YOSYS", "yosys")
    plugin = os.environ.get("AGCWS_SLANG_PLUGIN", "")
    if not plugin:
        raise SystemExit("AGCWS_SLANG_PLUGIN is required for the Ibex probe")
    read = (f"plugin -i {plugin}; read_slang --top {args.top} -D SYNTHESIS "
            + " ".join(f"-I {path}" for path in include_dirs)
            + " " + " ".join(source_paths))
    if args.map:
        read += (f"; hierarchy -top {args.top}; proc; opt; techmap; opt; "
                 f"dfflibmap -liberty {args.liberty}; abc -liberty {args.liberty}; "
                 f"clean; write_verilog -noattr -noexpr {args.out / 'mapped.v'}")
    args.out.mkdir(parents=True, exist_ok=True)
    # Keep frontend diagnostics in the artifact.  ``-Q`` hides the Slang error
    # location and turns a reproducibility failure into an opaque exit code.
    result = subprocess.run([yosys, "-p", read], capture_output=True, text=True,
                            check=False)
    stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    (args.out / "yosys.log").write_text("STDOUT\n" + stdout + "\nSTDERR\n" + stderr)
    (args.out / "manifest.json").write_text(json.dumps({
        "top": args.top, "sources": args.sources.resolve().as_posix(),
        "source_count": len(source_paths), "original_source_paths": original_paths,
        "resolved_source_paths": source_paths, "command": [yosys, "-p", read],
        "returncode": returncode,
        "map": args.map, "liberty": str(args.liberty) if args.map else None,
        "liberty_sha256": sha256(args.liberty) if args.map and args.liberty.is_file() else None,
        "sources_sha256": sha256(args.sources),
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "returncode": returncode,
                      "sources": len(source_paths)}, sort_keys=True))
    raise SystemExit(returncode)


if __name__ == "__main__":
    main()
