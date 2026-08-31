#!/usr/bin/env python3
"""Write reproducibility metadata for a paired AES PDK validation run."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def version(command: str, *args: str) -> str | None:
    try:
        result = subprocess.run([command, *args], check=True,
                                capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = (result.stdout or result.stderr).splitlines()
    return lines[0] if lines else ""


def synthesis_record(directory: Path, liberty: Path) -> dict:
    manifest = directory / "manifest.json"
    netlist = directory / "mapped.v"
    return {"manifest": str(manifest),
            "manifest_sha256": digest(manifest) if manifest.is_file() else None,
            "netlist_sha256": digest(netlist), "liberty": str(liberty),
            "liberty_sha256": digest(liberty),
            "synthesis_manifest": json.loads(manifest.read_text())}


def write(output: Path, corpus: Path, sky_synth: Path, nangate_synth: Path,
          sky_lib: Path, nangate_lib: Path) -> dict:
    workloads = sorted(corpus.glob("trial-*/workload.json"))
    payload = {
        "corpus": str(corpus), "workloads": len(workloads),
        "workload_sha256": [digest(path) for path in workloads],
        "waveform_sha256": [digest(path.parent / "activity.vcd") for path in workloads],
        "tools": {"opensta": version("sta", "-version"),
                  "yosys": version("yosys", "-V")},
        "synthesis": {"sky130hd": synthesis_record(sky_synth, sky_lib),
                      "nangate45": synthesis_record(nangate_synth, nangate_lib)},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("sky_synthesis", type=Path)
    parser.add_argument("nangate_synthesis", type=Path)
    parser.add_argument("sky_liberty", type=Path)
    parser.add_argument("nangate_liberty", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write(args.out, args.corpus, args.sky_synthesis,
                           args.nangate_synthesis, args.sky_liberty,
                           args.nangate_liberty), indent=2))


if __name__ == "__main__":
    main()
