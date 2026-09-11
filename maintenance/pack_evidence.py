"""One-time tracked-file packing; retire loose copies only after verified restoration."""

import argparse
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from agcws.pipeline.evidence import PACK, manifest, sha, verify


def tracked(repo):
    rows = subprocess.check_output(["git", "ls-files", "--stage", "-z", "results"], cwd=repo)
    result = {}
    for row in rows.split(b"\0"):
        if not row:
            continue
        meta, name = row.decode().split("\t", 1)
        mode, blob, stage = meta.split()
        if stage != "0" or mode not in ("100644", "100755"):
            raise ValueError("unmerged or nonregular tracked evidence")
        result[name] = (int(mode, 8) & 0o777, blob)
    return result


def blob(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def pack(repo, study, entries):
    root = repo / "results" / study
    if (root / PACK).exists():
        raise FileExistsError(root / PACK)
    output = {
        "version": 1,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip(),
        "files": {},
        "shards": {},
    }
    groups, group, size = [], [], 0
    for name, mode, oid in entries:
        path = root / name
        if path.resolve() != path:
            raise ValueError("symlink evidence")
        data = path.read_bytes()
        if blob(data) != oid:
            raise ValueError(f"working evidence differs from index: {path}")
        if group and size + len(data) > 32 * 1024 * 1024:
            groups.append(group)
            group, size = [], 0
        group.append(name)
        size += len(data)
        output["files"][name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
            "mode": mode,
            "git_blob": oid,
        }
    groups.append(group)
    for number, members in enumerate(groups):
        shard = f"evidence-{number:03}.tar.gz"
        with (root / shard).open("xb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(
                    fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT
                ) as archive:
                    for name in members:
                        data = (root / name).read_bytes()
                        if hashlib.sha256(data).hexdigest() != output["files"][name]["sha256"]:
                            raise ValueError("evidence changed during packing")
                        member = tarfile.TarInfo(name)
                        member.size = len(data)
                        member.mode = output["files"][name]["mode"]
                        archive.addfile(member, io.BytesIO(data))
        output["shards"][shard] = sha(root / shard)
    with (root / PACK).open("xb") as out:
        out.write(gzip.compress(json.dumps(output, sort_keys=True).encode(), mtime=0))
    with tempfile.TemporaryDirectory(prefix="agcws-pack-verify-") as temp:
        restored = Path(temp) / "restored"
        result = verify(root, restored)
        for name, meta in output["files"].items():
            if sha(restored / name) != sha(root / name) or sha(root / name) != meta["sha256"]:
                raise ValueError("round-trip mismatch")
    print(json.dumps(result), flush=True)


def retire(repo, study):
    root = repo / "results" / study
    verify(root)
    m = manifest(root)
    paths = []
    for name, meta in m["files"].items():
        path = root / name
        if not path.is_file() or path.resolve() != path or sha(path) != meta["sha256"]:
            raise ValueError(f"loose evidence changed: {path}")
        paths.append(path)
    # GNU find receives exact, validated regular-file paths, never a broad root.
    with tempfile.NamedTemporaryFile(prefix="agcws-packed-paths-") as listing:
        listing.write(b"\0".join(str(p).encode() for p in paths) + b"\0")
        listing.flush()
        subprocess.run(
            ["find", "-files0-from", listing.name, "-maxdepth", "0", "-type", "f", "-delete"],
            check=True,
        )
    if any(p.exists() for p in paths):
        raise ValueError("loose evidence retirement incomplete")
    subprocess.run(
        ["find", str(root), "-depth", "-mindepth", "1", "-type", "d", "-empty", "-delete"],
        check=True,
    )
    print(
        json.dumps({"study": study, "retired_loose_copies": len(paths), "recoverable": True}),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retire", action="store_true")
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    groups = {}
    for path, (mode, oid) in tracked(repo).items():
        parts = Path(path).parts
        if len(parts) > 3:
            groups.setdefault(parts[1], []).append((str(Path(*parts[2:])), mode, oid))
    for study, entries in sorted(groups.items()):
        if len(entries) > 500:
            retire(repo, study) if args.retire else pack(repo, study, entries)


if __name__ == "__main__":
    main()
