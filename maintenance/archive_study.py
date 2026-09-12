"""Pack a completed pipeline export, or restore its exact raw compact evidence."""

import argparse
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from agcws.pipeline import engine, evidence


def restore(source, destination):
    if destination.exists():
        raise FileExistsError(destination)
    with tempfile.TemporaryDirectory(prefix="agcws-restore-export-") as temp:
        compact = Path(temp) / "compact"
        evidence.verify(source, compact)
        engine.verify_export(compact)
        inventory = json.loads((compact / "inventory.json").read_text())
        destination.mkdir(parents=True)
        for name, expected in inventory.items():
            evidence.relative(name)
            data = gzip.decompress((compact / (name + ".gz")).read_bytes())
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("raw export differs")
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                output.write(data)
    return {"restored_files": len(inventory), "destination": str(destination)}


def pack(root, destination):
    if destination.exists():
        raise FileExistsError(destination)
    with tempfile.TemporaryDirectory(prefix="agcws-pack-export-") as temp:
        compact = Path(temp) / "compact"
        engine.export(root, compact)
        engine.verify_export(compact)
        destination.mkdir(parents=True)
        metadata = {
            "version": 1,
            "kind": "completed-pipeline-export",
            "producer_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "run_manifest_sha256": evidence.sha(root / "manifest.json"),
            "files": {},
            "shards": {},
        }
        shard = destination / "evidence-000.tar.gz"
        with shard.open("xb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(
                    fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT
                ) as archive:
                    for path in sorted(p for p in compact.rglob("*") if p.is_file()):
                        name = str(path.relative_to(compact))
                        evidence.relative(name)
                        data = path.read_bytes()
                        member = tarfile.TarInfo(name)
                        member.size, member.mode = len(data), 0o644
                        archive.addfile(member, io.BytesIO(data))
                        metadata["files"][name] = {
                            "sha256": hashlib.sha256(data).hexdigest(),
                            "size": len(data),
                            "mode": 0o644,
                        }
        metadata["shards"][shard.name] = evidence.sha(shard)
        with (destination / evidence.PACK).open("xb") as output:
            output.write(gzip.compress(json.dumps(metadata, sort_keys=True).encode(), mtime=0))
        result = restore(destination, Path(temp) / "restored")
        for path in (Path(temp) / "restored").rglob("*"):
            if path.is_file() and evidence.sha(path) != evidence.sha(
                root / path.relative_to(Path(temp) / "restored")
            ):
                raise ValueError("restored raw bytes differ from completed run")
    return {**result, "destination": str(destination), "raw_scratch_unchanged": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pack", "restore"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    action = pack if args.action == "pack" else restore
    print(json.dumps(action(args.source.resolve(), args.destination.resolve())))


if __name__ == "__main__":
    main()
