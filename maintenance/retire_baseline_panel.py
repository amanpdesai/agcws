"""Archive compact evidence, verify it, then losslessly retire exact baseline VCDs."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import subprocess
import tarfile
from functools import partial
from pathlib import Path

from agcws.pipeline.retention import command_digest, compact, file_digest
from agcws.pipeline.storage import ensure, read

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "out/baselines-maxbin-v1"


def retire_archived_fst(path, record_hash):
    """Reconstruct the measured waveform digest from a verified archive member."""
    fst, record = path.with_suffix(".fst"), path.parent / "activity.json"
    if any(p.resolve() != p or not p.is_file() for p in (path, fst, record)):
        raise ValueError("explicit nonsymlink retirement files required")
    data = record.read_bytes()
    if hashlib.sha256(data).hexdigest() != record_hash:
        raise ValueError("activity record differs from verified archive")
    activity = json.loads(data)
    if activity.get("vcd") != path.name or not isinstance(activity.get("waveform_sha256"), str):
        raise ValueError("archived activity must identify this waveform")
    before, fst_before = path.stat(), fst.stat()
    expected = (activity["waveform_sha256"], before.st_size)
    if command_digest(["fst2vcd", str(fst)]) != expected:
        raise ValueError("FST does not reproduce measured waveform")
    packed_hash, packed_size = file_digest(fst)
    for source, previous in ((path, before), (fst, fst_before)):
        current = source.stat()
        if (current.st_ino, current.st_size, current.st_mtime_ns) != (
                previous.st_ino, previous.st_size, previous.st_mtime_ns):
            raise ValueError("waveform changed during verification")
    receipt = {"version": 1, "source": path.name, "sha256": expected[0], "bytes": expected[1],
               "retained": fst.name, "encoding": "fst",
               "retained_sha256": packed_hash, "retained_bytes": packed_size}
    ensure(path.with_suffix(".vcd.retention.json"), receipt)
    subprocess.run(["find", "-P", str(path), "-maxdepth", "0", "-type", "f", "-delete"], check=True)
    if path.exists():
        raise RuntimeError("verified waveform was not retired")
    return receipt


def retire_or_verify(path, archived=None):
    if path.exists():
        if archived is not None and path.with_suffix(".fst").exists():
            name = str((path.parent / "activity.json").relative_to(PANEL))
            if name in archived:
                return retire_archived_fst(path, archived[name])
        return compact(path)
    receipt = read(path.with_suffix(".vcd.retention.json"))
    retained = path.parent / receipt["retained"]
    if retained.parent != path.parent or retained.is_symlink():
        raise ValueError("unsafe retained path")
    if file_digest(retained) != (receipt["retained_sha256"], receipt["retained_bytes"]):
        raise ValueError("retained waveform changed since retirement")
    return receipt


def archive(design):
    root = PANEL / design
    destination = ROOT / "out/retired-baselines-maxbin-v1"
    destination.mkdir(exist_ok=True)
    receipt = destination / f"{design}.json"
    archive_path = destination / f"{design}.tar.gz"
    if receipt.exists():
        return
    hashes = {}
    with tarfile.open(archive_path, "x:gz", compresslevel=1) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"symlink in evidence: {path}")
            if not path.is_file() or path.suffix not in (".json", ".log", ".S"):
                continue
            relative = str(path.relative_to(root))
            data = path.read_bytes()
            hashes[relative] = hashlib.sha256(data).hexdigest()
            archive.add(path, arcname=relative, recursive=False)
    verified = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            data = archive.extractfile(member).read()
            if hashlib.sha256(data).hexdigest() != hashes[member.name]:
                raise ValueError("archive mismatch")
            verified.add(member.name)
    if verified != set(hashes):
        raise ValueError("archive incomplete")
    ensure(receipt, {"files": hashes, "completed_cells": len(list(root.glob("panel/*/*/*/complete.json"))),
                     "panel_complete": (root / "complete.json").exists(),
                     "status": "historical; superseded by requested clean three-arm rerun"})
    print(f"{design}: verified {len(hashes)} compact evidence files", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        parser.error("workers must be 1..32")
    locks = []
    for design in ("aes", "dma", "ibex", "mesh", "redmule"):
        lock = (PANEL / design / "runner.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locks.append(lock)
    ids = subprocess.check_output(["docker", "ps", "-q"], text=True).split()
    if ids:
        containers = json.loads(subprocess.check_output(["docker", "inspect", *ids]))
        if any(str(PANEL) in m.get("Source", "") for c in containers for m in c["Mounts"]):
            raise ValueError("panel containers still active")
    for design in ("aes", "dma", "ibex", "mesh", "redmule"):
        archive(design)
    archived = {f"{design}/{name}": digest
                for design in ("aes", "dma", "ibex", "mesh", "redmule")
                for name, digest in read(ROOT / f"out/retired-baselines-maxbin-v1/{design}.json")["files"].items()}
    plan = ROOT / "out/retired-baselines-maxbin-v1/waveform-plan.json"
    if not plan.exists():
        ensure(plan, {"paths": [str(p.relative_to(PANEL)) for p in sorted(PANEL.glob("*/cache/**/*.vcd"))]})
    paths = [PANEL / p for p in read(plan)["paths"]]
    if any(p.resolve() != p or not p.is_relative_to(PANEL) or p.suffix != ".vcd" for p in paths):
        raise ValueError("unsafe retirement plan")
    reclaimed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, result in enumerate(pool.map(partial(retire_or_verify, archived=archived), paths), 1):
            reclaimed += result["bytes"]
            if index % 100 == 0:
                print(f"verified and retired {index}/{len(paths)} VCDs; raw bytes {reclaimed}", flush=True)
    ensure(ROOT / "out/retired-baselines-maxbin-v1/complete.json",
           {"retired_vcds": len(paths), "raw_bytes": reclaimed,
            "all_waveforms_retained_losslessly": True})


if __name__ == "__main__":
    main()
