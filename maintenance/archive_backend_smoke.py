"""Pack completed CPU-only backend smoke JSON without waveforms or build products."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from agcws.pipeline.storage import read, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    manifest = read(args.directory / "manifest.json")
    if set(manifest["spec"]["policies"]) != {"phase-random", "phase-ga"}:
        raise ValueError("this compact archive is only for the two CPU plumbing controls")
    complete = read(args.directory / "complete.json")
    files = {}
    for path in sorted(args.directory.rglob("*.json")):
        relative = path.relative_to(args.directory)
        if relative.parts[0] not in ("panel", "cache") and len(relative.parts) > 1:
            continue
        if path.is_symlink():
            raise ValueError("archive refuses symlinks")
        files[str(relative)] = path.read_text()
    bundle = {"scope": "CPU backend plumbing, not qualified targets or policy inference",
              "source_commit": args.source_commit, "files": files}
    blob = gzip.compress(json.dumps(bundle, sort_keys=True).encode(), mtime=0)
    args.destination.mkdir(parents=True, exist_ok=True)
    with (args.destination / "shared_panel.json.gz").open("xb") as stream:
        stream.write(blob)
    write(args.destination / "shared_panel_summary.json", {
        "scope": bundle["scope"], "source_commit": args.source_commit,
        "archive_sha256": hashlib.sha256(blob).hexdigest(), "complete": complete,
        "files": len(files), "model_calls": 0,
    })


if __name__ == "__main__":
    main()
