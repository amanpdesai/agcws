"""Archive all refinement checkpoints and publish a separately versioned mesh bank."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from audit_mesh_refinement import audit

from agcws.pipeline.storage import read, write


def archive(root, destination):
    receipt = audit(root)
    destination.mkdir(parents=True, exist_ok=False)
    paths = [root / "manifest.json", root / "complete.json",
             *root.glob("panel/*/*.json"), *root.glob("cache/*/result.json")]
    bundle = {}
    for path in sorted(paths):
        raw = path.read_bytes()
        bundle[str(path.relative_to(root))] = {"sha256": hashlib.sha256(raw).hexdigest(),
                                              "text": raw.decode()}
    raw = json.dumps(bundle, sort_keys=True).encode()
    compressed = gzip.compress(raw, mtime=0)
    if gzip.decompress(compressed) != raw:
        raise ValueError("archive roundtrip failed")
    with (destination / "evidence.json.gz").open("xb") as stream:
        stream.write(compressed)
    manifest = read(root / "manifest.json")
    source = Path(manifest["reference"]).parent
    bank = read(source / "qualification/requested-bank.json")
    original = read(source / "qualification/admission.json")
    refined = read(root / "complete.json")
    replacements = {r["id"]: r for r in refined["outcomes"]}
    witnesses = []
    for outcome in original["outcomes"]:
        if outcome["qualified"]:
            witnesses.append({"id": outcome["id"], "source": "bit-activity-v2",
                              "witness": outcome["witness"]})
        else:
            row = replacements[outcome["id"]]
            if not row["qualified"]:
                raise ValueError("mesh bank still incomplete")
            witnesses.append({"id": row["id"], "source": "local-refinement-v1", "witness": row})
    write(destination / "bank.json", {**bank, "version": "mesh-bit-refinement-v1",
          "task_bank_qualified": True, "full_study_ready": False, "qualified": 18,
          "witnesses": witnesses, "original_qualified": 14,
          "additional_charged_slots": 2048, "scope": "post-hoc witness engineering, not policy comparison"})
    write(destination / "audit.json", {**receipt, "archived_files": len(bundle),
          "evidence_sha256": hashlib.sha256(compressed).hexdigest()})
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(archive(args.root.resolve(), args.destination.resolve())))
