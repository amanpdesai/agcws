"""Pack a completed pipeline export, or restore its exact raw compact evidence."""

import argparse
import contextlib
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from agcws.evidence import packs as evidence
from agcws.studies import engine


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


def shard_groups(paths, maximum):
    if type(maximum) is not int or maximum <= 65536:
        raise ValueError("shard limit must exceed 64 KiB")
    groups, current, size = [], [], 0
    for path in paths:
        member_size = 512 + ((path.stat().st_size + 511) // 512) * 512
        if member_size > maximum - 65536:
            raise ValueError(f"individual evidence member exceeds shard limit: {path.name}")
        if current and size + member_size > maximum - 65536:
            groups.append(current)
            current, size = [], 0
        current.append(path)
        size += member_size
    if current:
        groups.append(current)
    return groups


def pack(root, destination, max_shard_bytes=32 * 1024 * 1024):
    if destination.exists():
        raise FileExistsError(destination)
    if not (root / "complete.json").exists():
        raise ValueError("only complete studies can be exported")
    if type(max_shard_bytes) is not int or max_shard_bytes <= 65536:
        raise ValueError("shard limit must exceed 64 KiB")
    paths = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("export refuses symlinks")
        relative = path.relative_to(root)
        if (path.is_file() and path.suffix in (".json", ".log", ".S")
                and not path.name.startswith("trace_")
                and (relative.parts[0] in ("panel", "cache") or len(relative.parts) == 1)):
            paths.append(path)
    destination.mkdir(parents=True)
    metadata = {"version": 1, "kind": "completed-pipeline-export",
                "producer_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "run_manifest_sha256": evidence.sha(root / "manifest.json"),
                "files": {}, "shards": {}}
    hashes = {}
    stack = contextlib.ExitStack()
    archive, shard, size, index = None, None, 0, 0

    def close_shard():
        stack.close()
        if shard is not None:
            if shard.stat().st_size > max_shard_bytes:
                raise ValueError("compressed shard exceeds requested size limit")
            metadata["shards"][shard.name] = evidence.sha(shard)

    def member(name, data):
        nonlocal archive, shard, size, index, stack
        evidence.relative(name)
        member_size = 512 + ((len(data) + 511) // 512) * 512
        if member_size > max_shard_bytes - 65536:
            raise ValueError(f"individual evidence member exceeds shard limit: {name}")
        if archive is None or size + member_size > max_shard_bytes - 65536:
            close_shard()
            stack = contextlib.ExitStack()
            shard = destination / f"evidence-{index:03}.tar.gz"
            index += 1
            raw = stack.enter_context(shard.open("xb"))
            compressed = stack.enter_context(gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0))
            archive = stack.enter_context(tarfile.open(fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT))
            size = 0
        item = tarfile.TarInfo(name)
        item.size, item.mode = len(data), 0o644
        archive.addfile(item, io.BytesIO(data))
        size += member_size
        metadata["files"][name] = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "mode": 0o644}

    try:
        for path in paths:
            name = str(path.relative_to(root))
            raw = path.read_bytes()
            hashes[name] = hashlib.sha256(raw).hexdigest()
            member(name + ".gz", gzip.compress(raw, mtime=0))
        member("inventory.json", (json.dumps(hashes, indent=2) + "\n").encode())
        close_shard()
    finally:
        stack.close()
    with (destination / evidence.PACK).open("xb") as output:
        output.write(gzip.compress(json.dumps(metadata, sort_keys=True).encode(), mtime=0))
    evidence.verify(destination)
    seen = set()
    for shard_name in metadata["shards"]:
        with tarfile.open(destination / shard_name, "r|gz") as packed:
            for item in packed:
                data = packed.extractfile(item).read()
                if item.name == "inventory.json":
                    if json.loads(data) != hashes:
                        raise ValueError("restored inventory differs")
                    continue
                name = item.name[:-3]
                raw = gzip.decompress(data)
                if hashlib.sha256(raw).hexdigest() != hashes[name] or raw != (root / name).read_bytes():
                    raise ValueError("restored raw bytes differ from completed run")
                seen.add(name)
    if seen != set(hashes):
        raise ValueError("restored export is incomplete")
    return {"restored_files": len(hashes), "destination": str(destination),
            "raw_scratch_unchanged": True, "verification": "streamed exact-byte restoration"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pack", "restore"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--max-shard-mib", type=int, default=32,
                        help="pack-only bound; 64 supports large full-panel indexes")
    args = parser.parse_args(argv)
    if not 1 <= args.max_shard_mib <= 64:
        parser.error("shard bound must be between 1 and 64 MiB")
    if args.action == "restore":
        result = restore(args.source.resolve(), args.destination.resolve())
    else:
        result = pack(args.source.resolve(), args.destination.resolve(), args.max_shard_mib*1024*1024)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
