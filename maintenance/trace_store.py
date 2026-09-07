"""Verified content-addressed cold traces; retirement uses exact-path find."""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from maintenance.clean_artifacts import (
    REPO,
    active_references,
    checked_file,
    fingerprint,
    target_path,
)
from maintenance.find_delete import execute_find


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def decoded_digest(path):
    result, size = hashlib.sha256(), 0
    with tempfile.TemporaryFile() as errors:
        with subprocess.Popen(
            ["zstd", "-q", "-d", "-c", str(path)], stdout=subprocess.PIPE, stderr=errors
        ) as process:
            for chunk in iter(lambda: process.stdout.read(1024 * 1024), b""):
                result.update(chunk)
                size += len(chunk)
            status = process.wait()
        if status:
            errors.seek(0)
            raise ValueError(
                f"corrupt compressed trace: {errors.read().decode(errors='replace')}"
            )
    return result.hexdigest(), size


def pack_file(source, objects):
    before = fingerprint(source)
    identity = digest(source)
    destination = objects / identity[:2] / (identity + ".zst")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise ValueError("object is a symlink")
    if not destination.exists():
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, prefix=".pack-"
        ) as temporary:
            subprocess.run(
                ["zstd", "-q", "-3", "-T2", "-c", str(source)],
                stdout=temporary,
                check=True,
            )
            temporary.flush()
            os.fsync(temporary.fileno())
            if decoded_digest(Path(temporary.name)) != (identity, before[2]):
                raise ValueError("compression round-trip differs")
            try:
                os.link(temporary.name, destination)
            except FileExistsError:
                pass
    if (
        decoded_digest(destination) != (identity, before[2])
        or fingerprint(source) != before
    ):
        raise ValueError("object mismatch or source changed during compression")
    return {
        "sha256": identity,
        "raw_bytes": before[2],
        "fingerprint": before,
        "object": str(destination),
        "compressed_sha256": digest(destination),
        "compressed_bytes": destination.stat().st_size,
    }


def verify_object(entry):
    path = Path(entry["object"])
    if path.is_symlink() or digest(path) != entry["compressed_sha256"]:
        raise ValueError("compressed object changed")
    if decoded_digest(path) != (entry["sha256"], entry["raw_bytes"]):
        raise ValueError("decompressed object differs")


def pack(plan_path, index_path):
    plan = json.loads(plan_path.read_text())
    root = REPO / "out"
    if root.is_symlink() or plan["root"] != str(root) or index_path.exists():
        raise ValueError("wrong root or existing index")
    for target in plan["targets"]:
        target_path(root, target)
    if active_references(root, plan["targets"]):
        raise ValueError("active run")
    objects = root / "trace-objects/sha256"
    if objects.resolve() != objects:
        raise ValueError("symlink in object store path")
    entries = []
    for record in plan["files"]:
        source = checked_file(root, record, plan["targets"])
        entry = pack_file(source, objects)
        entries.append({"path": record["path"], **entry})
    result = {
        "format": "agcws-trace-objects-v1",
        "plan": str(plan_path),
        "plan_sha256": digest(plan_path),
        "root": str(root),
        "targets": plan["targets"],
        "entries": entries,
        "raw_bytes": sum(e["raw_bytes"] for e in entries),
        "unique_compressed_bytes": sum(
            e["compressed_bytes"] for e in {e["sha256"]: e for e in entries}.values()
        ),
        "zstd_version": subprocess.check_output(
            ["zstd", "--version"], text=True
        ).strip(),
        "state": "Verified archive; original files not removed by pack.",
    }
    with index_path.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "entries"}), flush=True)


def retire(index_path):
    index = json.loads(index_path.read_text())
    plan_path = Path(index["plan"])
    if digest(plan_path) != index["plan_sha256"] or index["root"] != str(REPO / "out"):
        raise ValueError("changed plan or root")
    plan = json.loads(plan_path.read_text())
    if index["targets"] != plan["targets"] or [e["path"] for e in index["entries"]] != [
        e["path"] for e in plan["files"]
    ]:
        raise ValueError("archive does not cover exact plan")
    for entry in index["entries"]:
        expected = (
            REPO
            / "out/trace-objects/sha256"
            / entry["sha256"][:2]
            / (entry["sha256"] + ".zst")
        )
        if Path(entry["object"]) != expected or expected.resolve() != expected:
            raise ValueError("object outside verified store")
        verify_object(entry)
    for target in index["targets"]:
        target_path(REPO / "out", target)
    if active_references(REPO / "out", index["targets"]):
        raise ValueError("active run")
    tracked = set(
        subprocess.check_output(["git", "ls-files", "-z", "out"], cwd=REPO)
        .decode()
        .split("\0")
    )
    paths = [checked_file(REPO / "out", e, index["targets"]) for e in index["entries"]]
    if any(
        str(p.relative_to(REPO)) in tracked
        or not os.access(p.parent, os.W_OK | os.X_OK)
        for p in paths
    ):
        raise ValueError("tracked or unwritable trace")
    allocated = sum(p.stat().st_blocks * 512 for p in paths)
    deleted = execute_find(
        paths,
        index_path.with_suffix(".retired.jsonl"),
        index_path.with_suffix(".retire-input.nul"),
    )
    print(
        json.dumps(
            {
                "retired_files": len(deleted),
                "removed_allocated_bytes": allocated,
                "recovery": "Restore byte-identical originals from the index and compressed objects.",
            }
        ),
        flush=True,
    )


def restore(index_path, name, destination):
    index = json.loads(index_path.read_text())
    matches = [e for e in index["entries"] if e["path"] == name]
    if len(matches) != 1:
        raise ValueError("missing or duplicate trace identity")
    entry = matches[0]
    verify_object(entry)
    if destination.is_symlink():
        raise ValueError("refusing symlink destination")
    if destination.exists():
        if digest(destination) == entry["sha256"]:
            return
        raise ValueError("refusing to overwrite different existing data")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, prefix=".restore-"
    ) as temporary:
        subprocess.run(
            ["zstd", "-q", "-d", "-c", entry["object"]], stdout=temporary, check=True
        )
        temporary.flush()
        os.fsync(temporary.fileno())
        if digest(Path(temporary.name)) != entry["sha256"]:
            raise ValueError("restoration checksum mismatch")
        os.link(temporary.name, destination)
    print("TRACE_RESTORED", destination, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    packing = commands.add_parser("pack")
    packing.add_argument("--plan", type=Path, required=True)
    packing.add_argument("--index", type=Path, required=True)
    retiring = commands.add_parser("retire")
    retiring.add_argument("--index", type=Path, required=True)
    restoring = commands.add_parser("restore")
    restoring.add_argument("--index", type=Path, required=True)
    restoring.add_argument("--path", required=True)
    restoring.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "pack":
        pack(args.plan, args.index)
    elif args.command == "retire":
        retire(args.index)
    else:
        restore(args.index, args.path, args.destination)
