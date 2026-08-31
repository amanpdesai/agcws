#!/usr/bin/env python3
"""Resolve and fingerprint the pinned Ibex RTL closure through FuseSoC."""
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
    parser.add_argument("--fusesoc", default=os.environ.get("AGCWS_FUSESOC", "fusesoc"))
    args = parser.parse_args()
    root = args.ibex_root.resolve()
    subprocess.run([
        args.fusesoc, "--cores-root=.", "run", "--target=lint", "--setup",
        args.core,
    ], cwd=root, check=True)
    manifest = find_eda_manifest(root / "build", args.core)
    sources, include_dirs = resolve_manifest(manifest)
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
