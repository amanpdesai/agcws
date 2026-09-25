"""Lossless waveform retirement after a durable evaluation checkpoint."""

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

from agcws.core.storage import ensure


def digest(stream):
    value, size = hashlib.sha256(), 0
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(chunk)
        size += len(chunk)
    return value.hexdigest(), size


def file_digest(path):
    with path.open("rb") as stream:
        return digest(stream)


def command_digest(command):
    with tempfile.TemporaryFile() as errors:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors) as process:
            result = digest(process.stdout)
            code = process.wait()
        if code:
            errors.seek(0)
            raise RuntimeError(f"trace conversion failed: {errors.read().decode(errors='replace')}")
    return result


def compact(vcd):
    """Caller holds the evaluation lock. Never discard the sole waveform copy."""
    vcd = Path(vcd).absolute()
    if vcd.resolve() != vcd or vcd.suffix != ".vcd" or not vcd.is_file():
        raise ValueError("explicit nonsymlink VCD required")
    before = vcd.stat()
    original = file_digest(vcd)
    fst = vcd.with_suffix(".fst")
    if fst.exists():
        if fst.is_symlink():
            raise ValueError("symlink FST")
        retained = fst
        restored = command_digest(["fst2vcd", str(fst)])
        encoding = "fst"
    else:
        retained = vcd.with_suffix(".vcd.zst")
        if retained.is_symlink():
            raise ValueError("symlink compressed trace")
        if not retained.exists():
            with tempfile.NamedTemporaryFile(dir=vcd.parent, prefix=".trace-") as temporary:
                subprocess.run(["zstd", "-q", "-1", "-c", str(vcd)], stdout=temporary, check=True)
                temporary.flush()
                os.fsync(temporary.fileno())
                if command_digest(["zstd", "-qdc", temporary.name]) != original:
                    raise ValueError("compression round-trip differs")
                os.link(temporary.name, retained)
        restored = command_digest(["zstd", "-qdc", str(retained)])
        encoding = "zstd"
    if restored != original:
        raise ValueError("retained waveform does not reproduce exact VCD bytes")
    packed_hash, packed_size = file_digest(retained)
    after = vcd.stat()
    if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
            before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns):
        raise ValueError("waveform changed during verification")
    receipt = {"version": 1, "source": vcd.name, "sha256": original[0], "bytes": original[1],
               "retained": retained.name, "encoding": encoding,
               "retained_sha256": packed_hash, "retained_bytes": packed_size}
    ensure(vcd.with_suffix(".vcd.retention.json"), receipt)
    subprocess.run(["find", "-P", str(vcd), "-maxdepth", "0", "-type", "f", "-delete"], check=True)
    if vcd.exists():
        raise RuntimeError("verified waveform was not retired")
    return receipt


def finalize(directory, checkpoint):
    """Only completed evaluations are eligible; failed/incomplete attempts remain inspectable."""
    if not checkpoint.is_file():
        raise ValueError("result checkpoint required before retention")
    with checkpoint.open("rb") as stream:
        os.fsync(stream.fileno())
    for vcd in sorted(directory.rglob("*.vcd")):
        compact(vcd)
