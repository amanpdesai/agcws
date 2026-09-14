"""Publish a per-design bit bank with compact, independently checkable inputs."""

import argparse
import gzip
import hashlib
import json
import runpy
from pathlib import Path

from admit_bit_bank import audit

from agcws.config import ROOT
from agcws.pipeline.storage import read, write


def archive(root, destination):
    audit(root)
    destination.mkdir(parents=True, exist_ok=False)
    pack = runpy.run_path(ROOT / "maintenance/archive_study.py")["pack"]
    pack(root / "replay", destination / "fixed-replay")
    for split in ("development", "confirmation"):
        panel = root / "qualification" / split
        if panel.exists():
            pack(panel, destination / f"witness-search-{split}")
    paths = [*root.glob("*.json"), root / "reference/manifest.json",
             *root.joinpath("qualification").glob("*.json"), root / "replay/complete.json"]
    bundle = {}
    for path in sorted(paths):
        raw = path.read_bytes()
        bundle[str(path.relative_to(root))] = {"sha256": hashlib.sha256(raw).hexdigest(),
                                              "text": raw.decode()}
    data = json.dumps(bundle, sort_keys=True, allow_nan=False).encode()
    with (destination / "inputs.json.gz").open("xb") as output:
        output.write(gzip.compress(data, mtime=0))
    admission = read(root / "qualification/admission.json")
    bank = read(root / "qualification/requested-bank.json")
    write(destination / "bank.json", {**bank, "admission": admission,
                                     "task_bank_qualified": admission["task_bank_qualified"]})
    return {"destination": str(destination), "qualified": admission["qualified"],
            "input_files": len(bundle), "full_study_ready": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(archive(args.root.resolve(), args.destination.resolve())))
