#!/usr/bin/env python3
"""Resolve and fingerprint the pinned Ibex RTL closure through FuseSoC."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_manifest(manifest: Path) -> tuple[list[dict[str, str | int]], list[str]]:
    """Return hashed RTL files and include directories from a FuseSoC manifest."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to resolve FuseSoC sources") from exc
    document = yaml.safe_load(manifest.read_text())
    sources = []
    include_dirs = set()
    for entry in document.get("files", []):
        if entry.get("file_type") not in {"systemVerilogSource", "verilogSource"}:
            continue
        path = manifest.parent / entry["name"]
        if not path.is_file():
            raise FileNotFoundError(f"FuseSoC source is missing: {path}")
        include_dirs.add(str(path.parent.resolve()))
        if path.suffix not in {".sv", ".v"}:
            continue
        sources.append({"path": str(path.resolve()), "sha256": sha256(path),
                        "bytes": path.stat().st_size})
    if not sources:
        raise ValueError(f"FuseSoC manifest has no SystemVerilog sources: {manifest}")
    return sources, sorted(include_dirs)


def require_toplevel(sources: list[dict[str, str | int]], top: str) -> None:
    """Reject a FuseSoC closure that does not contain its declared top module."""
    module = f"module {top}"
    if not any(module in Path(str(item["path"])).read_text(errors="ignore")
               for item in sources):
        raise ValueError(
            f"resolved closure does not contain top-level module {top}; "
            "the selected FuseSoC target may omit its RTL fileset"
        )


def add_toplevel_fallback(root: Path, top: str, sources: list[dict[str, str | int]],
                          include_dirs: list[str]) -> None:
    """Add a checked-out top RTL file when a generated lint closure omits it."""
    if any(f"module {top}" in Path(str(item["path"])).read_text(errors="ignore")
           for item in sources):
        return
    candidates = [root / "rtl" / f"{top}.sv", root / "rtl" / f"{top}.v"]
    for path in candidates:
        if path.is_file():
            sources.append({"path": str(path.resolve()), "sha256": sha256(path),
                            "bytes": path.stat().st_size})
            if str(path.parent.resolve()) not in include_dirs:
                include_dirs.append(str(path.parent.resolve()))
            return


def add_include_root(path: Path, include_dirs: list[str]) -> None:
    """Record an optional include-only directory without requiring its files."""
    resolved = path.resolve()
    if resolved.is_dir() and str(resolved) not in include_dirs:
        include_dirs.append(str(resolved))


def add_include_file_dirs(root: Path, filenames: tuple[str, ...],
                          include_dirs: list[str]) -> None:
    """Add every generated directory containing an include-only file."""
    for filename in filenames:
        for path in root.rglob(filename):
            add_include_root(path.parent, include_dirs)


def add_source_file(path: Path, sources: list[dict[str, str | int]],
                    include_dirs: list[str]) -> None:
    """Add a required RTL source omitted by a generated target manifest."""
    path = path.resolve()
    if not path.is_file() or path.suffix not in {".sv", ".v"}:
        return
    if not any(item["path"] == str(path) for item in sources):
        sources.insert(0, {"path": str(path), "sha256": sha256(path),
                           "bytes": path.stat().st_size})
    add_include_root(path.parent, include_dirs)


def add_declared_fileset(core_file: Path, fileset: str, sources: list[dict[str, str | int]],
                         include_dirs: list[str]) -> None:
    """Add direct files from an Ibex core fileset omitted by a lint target."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to resolve FuseSoC sources") from exc
    document = yaml.safe_load(core_file.read_text())
    entries = document.get("filesets", {}).get(fileset, {}).get("files", [])
    known = {item["path"] for item in sources}
    for entry in entries:
        name = entry if isinstance(entry, str) else next(iter(entry))
        path = (core_file.parent / name).resolve()
        if path.suffix not in {".sv", ".v"}:
            continue
        if not path.is_file():
            raise FileNotFoundError(f"FuseSoC fileset source is missing: {path}")
        if str(path) not in known:
            sources.append({"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size})
            known.add(str(path))
        if str(path.parent) not in include_dirs:
            include_dirs.append(str(path.parent))


def find_eda_manifest(build_root: Path, core_id: str) -> Path:
    """Find the lint EDA manifest emitted for a FuseSoC core ID.

    FuseSoC may emit manifests for both lint and simulation setup.  The lint
    manifest is the source-of-truth closure for synthesis and fingerprinting.
    """
    leaf = core_id.split(":")[-1]
    # FuseSoC prefixes generated filenames with vendor and library, e.g.
    # ``lowrisc_ibex_ibex_simple_system_0.eda.yml``.
    matches = sorted(build_root.glob(f"**/*{leaf}_*.eda.yml"))
    lint_matches = [path for path in matches if path.parent.name == "lint-verilator"]
    if len(lint_matches) == 1:
        return lint_matches[0]
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected one lint EDA manifest for {core_id}, found "
            f"{len(lint_matches)} among {len(matches)} manifests"
        )
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ibex-root", type=Path, default=Path("third_party/ibex"))
    parser.add_argument("--out", type=Path, default=Path("out/ibex-sources"))
    parser.add_argument("--core", default="lowrisc:ibex:ibex_simple_system")
    default_fusesoc = Path(sys.executable).with_name("fusesoc")
    if not default_fusesoc.is_file():
        default_fusesoc = Path("fusesoc")
    parser.add_argument("--fusesoc", default=os.environ.get("AGCWS_FUSESOC", str(default_fusesoc)))
    args = parser.parse_args()
    root = args.ibex_root.resolve()
    # Keep FuseSoC's generated export outside the RTL checkout.  This avoids
    # stale/root-owned artifacts left by container builds and makes repeated
    # resolution safe on a normal host checkout.
    fusesoc_work_root = args.out.resolve().parent / "fusesoc-work"
    subprocess.run([
        args.fusesoc, "--cores-root=.", "run", "--work-root", str(fusesoc_work_root),
        "--target=lint", "--setup",
        args.core,
    ], cwd=root, check=True)
    manifest = find_eda_manifest(fusesoc_work_root, args.core)
    sources, include_dirs = resolve_manifest(manifest)
    top = manifest.read_text().split("toplevel:", 1)[1].splitlines()[0].strip()
    if not any(f"module {top}" in Path(str(item["path"])).read_text(errors="ignore")
               for item in sources):
        for core_file in ("ibex_pkg.core", "ibex_core.core", "ibex_top.core"):
            add_declared_fileset(root / core_file, "files_rtl", sources, include_dirs)
    add_toplevel_fallback(root, top, sources, include_dirs)
    add_include_root(root / "vendor/lowrisc_ip/dv/sv/dv_utils", include_dirs)
    add_include_file_dirs(root, ("prim_util_memload.svh", "dv_fcov_macros.svh"), include_dirs)
    # add_source_file prepends; list consumers first so packages end up first.
    for package in ("prim_secded_pkg.sv", "prim_util_pkg.sv", "prim_cipher_pkg.sv",
                    "prim_count.sv", "prim_count_pkg.sv"):
        add_source_file(root / "vendor/lowrisc_ip/ip/prim/rtl" / package,
                        sources, include_dirs)
    require_toplevel(sources, top)
    args.out.mkdir(parents=True, exist_ok=True)
    output = args.out / "sources.json"
    output.write_text(json.dumps({
        "design": args.core,
        "manifest": str(manifest),
        "include_dirs": include_dirs,
        "sources": sources,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"sources": len(sources), "manifest": str(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
