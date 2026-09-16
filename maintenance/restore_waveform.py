"""Restore a retained waveform to an explicit new file, verifying both hashes."""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from agcws.pipeline.retention import file_digest


def restore(receipt_path, destination):
    receipt_path, destination = Path(receipt_path), Path(destination)
    receipt = json.loads(receipt_path.read_text())
    name = receipt["retained"]
    if Path(name).name != name or name in (".", ".."):
        raise ValueError("retained filename must be local")
    retained = receipt_path.parent / name
    if retained.is_symlink() or file_digest(retained) != (receipt["retained_sha256"], receipt["retained_bytes"]):
        raise ValueError("retained waveform checksum mismatch")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    commands = {"fst": ["fst2vcd", str(retained)], "zstd": ["zstd", "-qdc", str(retained)]}
    if receipt["encoding"] not in commands:
        raise ValueError("unsupported trace encoding")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".restore-") as stream:
        subprocess.run(commands[receipt["encoding"]], stdout=stream, check=True)
        stream.flush()
        os.fsync(stream.fileno())
        if file_digest(Path(stream.name)) != (receipt["sha256"], receipt["bytes"]):
            raise ValueError("restored waveform checksum mismatch")
        os.link(stream.name, destination)
    return {"destination": str(destination), "sha256": receipt["sha256"], "bytes": receipt["bytes"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(restore(args.receipt, args.destination)))


if __name__ == "__main__":
    main()
