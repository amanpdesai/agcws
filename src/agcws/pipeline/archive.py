"""Verified historical sources, explicitly isolated from the maintained runtime."""

import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from agcws.pipeline import evidence


def verify(repo):
    manifest = json.loads((repo / "archive/manifest.json").read_text())
    source = repo / "archive/legacy-source.tar.gz"
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest["archive_sha256"]:
        raise ValueError("historical source archive hash differs")
    actual = {}
    with tarfile.open(source) as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if (
                not path.parts
                or path.is_absolute()
                or ".." in path.parts
                or not (member.isdir() or member.isfile())
            ):
                raise ValueError(f"unsafe archive member: {member.name}")
            if member.isfile():
                if member.name in actual:
                    raise ValueError("duplicate archive member")
                actual[member.name] = hashlib.sha256(archive.extractfile(member).read()).hexdigest()
    if actual != manifest["files"]:
        raise ValueError("archive file inventory differs")
    return manifest


def extract(repo, destination):
    verify(repo)
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(repo / "archive/legacy-source.tar.gz") as archive:
        for member in archive:
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(archive.extractfile(member).read())
                target.chmod(member.mode & 0o777)
    return destination


def audit(repo, python):
    # An isolated source tree with read-only *use* of existing evidence/dependencies.
    # The frozen audit has no evaluation or provider-call entry point.
    with tempfile.TemporaryDirectory(prefix="agcws-archive-audit-") as temp:
        destination = extract(repo, Path(temp) / "source")
        review = evidence.materialize(repo, Path(temp) / "review", ["nonflat_temporal_v1"])
        (destination / "results").symlink_to(review / "results", target_is_directory=True)
        for name in ("third_party", "tools"):
            (destination / name).symlink_to(repo / name, target_is_directory=True)
        env = {
            **os.environ,
            "PYTHONPATH": str(destination / "src"),
            "OPENBLAS_NUM_THREADS": "1",
        }
        return subprocess.run(
            [
                str(python),
                "-c",
                (
                    "import json; from pathlib import Path; from experiments.nonflat_temporal_v1.audit import audit; "
                    "from experiments.ibex_depth_v1.storage import read; "
                    "p=Path('results/nonflat_temporal_v1'); s=audit(p); "
                    "assert s==read(p/'summary.json'); "
                    "print(json.dumps({'audit':'passed','cells':s['cells'],'slots':s['slots']}))"
                ),
            ],
            cwd=destination,
            env=env,
            check=True,
        ).returncode
