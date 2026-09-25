"""Lossless packed evidence and isolated, original-path review workspaces."""

import gzip
import hashlib
import json
import tarfile
from pathlib import PurePosixPath

PACK = "evidence.pack.json.gz"


def sha(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or ".." in path.parts or str(path) != name:
        raise ValueError(f"unsafe evidence path: {name}")
    return path


def manifest(study):
    result = json.loads(gzip.decompress((study / PACK).read_bytes()))
    if result["version"] != 1:
        raise ValueError("unsupported evidence format")
    for name in result["files"]:
        relative(name)
    for name in result["shards"]:
        if len(relative(name).parts) != 1:
            raise ValueError("shard must be in study root")
    return result


def verify(study, destination=None):
    """Check every member; optionally restore regular files into a new directory."""
    m = manifest(study)
    for name, checksum in m["shards"].items():
        if sha(study / name) != checksum:
            raise ValueError(f"shard checksum differs: {name}")
    seen = set()
    if destination is not None:
        destination.mkdir(parents=True, exist_ok=False)
    for shard in m["shards"]:
        with tarfile.open(study / shard, "r|gz") as archive:
            for member in archive:
                relative(member.name)
                if not member.isfile() or member.name in seen or member.name not in m["files"]:
                    raise ValueError("unexpected, duplicate or nonregular evidence member")
                expected = m["files"][member.name]
                if member.size != expected["size"] or member.mode != expected["mode"]:
                    raise ValueError("member size/mode differs")
                data = archive.extractfile(member).read()
                if hashlib.sha256(data).hexdigest() != expected["sha256"]:
                    raise ValueError("member checksum differs")
                seen.add(member.name)
                if destination is not None:
                    target = destination / member.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as out:
                        out.write(data)
                    target.chmod(member.mode)
    if seen != set(m["files"]):
        raise ValueError("incomplete evidence inventory")
    return {"study": study.name, "files": len(seen), "verified": True}


def read_selected(study, names):
    """Read selected exact members without unpacking a study onto disk."""
    m = manifest(study)
    requested = set(names)
    if not requested <= set(m["files"]):
        raise ValueError("requested evidence is absent from inventory")
    result = {}
    for shard, checksum in m["shards"].items():
        if sha(study / shard) != checksum:
            raise ValueError(f"shard checksum differs: {shard}")
        with tarfile.open(study / shard, "r|gz") as archive:
            for member in archive:
                relative(member.name)
                if member.name not in requested:
                    continue
                if not member.isfile() or member.name in result:
                    raise ValueError("duplicate or nonregular selected member")
                expected = m["files"][member.name]
                data = archive.extractfile(member).read()
                if (member.size != expected["size"] or member.mode != expected["mode"]
                        or hashlib.sha256(data).hexdigest() != expected["sha256"]):
                    raise ValueError("selected member differs from inventory")
                result[member.name] = data
    if set(result) != requested:
        raise ValueError("missing selected evidence member")
    return result


def studies(repo):
    return sorted(p.parent.name for p in (repo / "results").glob(f"*/{PACK}"))


def materialize(repo, destination, selected):
    """Restore chosen studies; link unmodified local sources and other evidence.

    A review view is disposable, not an independent export. Nonpacked files are
    symlinked to the checkout, so callers must treat them as read-only.
    """
    known = set(studies(repo))
    if not selected or not set(selected) <= known:
        raise ValueError("select existing packed studies")
    destination.mkdir(parents=True, exist_ok=False)
    for source in repo.iterdir():
        if source.name not in ("results", ".git"):
            (destination / source.name).symlink_to(
                source.resolve(), target_is_directory=source.is_dir()
            )
    results = destination / "results"
    results.mkdir()
    for source in (repo / "results").iterdir():
        target = results / source.name
        if source.name not in selected:
            target.symlink_to(source.resolve(), target_is_directory=source.is_dir())
            continue
        m = manifest(source)
        verify(source, target)
        for path in source.rglob("*"):
            rel = str(path.relative_to(source))
            if path.is_dir() or rel in m["files"] or rel == PACK or rel in m["shards"]:
                continue
            output = target / rel
            output.parent.mkdir(parents=True, exist_ok=True)
            output.symlink_to(path.resolve())
    return destination
