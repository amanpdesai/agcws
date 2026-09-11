import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from agcws.pipeline import archive


def test_historical_snapshot_inventory_and_isolated_extraction(tmp_path):
    repo = Path.cwd()
    manifest = archive.verify(repo)
    retired = json.loads((repo / "archive/retired-files.json").read_text())
    assert retired and all(manifest["files"][p] == digest for p, digest in retired.items())
    destination = tmp_path / "historical"
    archive.extract(repo, destination)
    assert (destination / "experiments/nonflat_temporal_v1/audit.py").is_file()
    assert (destination / "docs/NONFLAT_TEMPORAL_V1_PROTOCOL.md").is_file()
    assert (destination / "tests/test_nonflat_temporal_v1.py").is_file()
    with pytest.raises(FileExistsError):
        archive.extract(repo, destination)


@pytest.mark.parametrize(
    "name,kind",
    [("../escape", tarfile.REGTYPE), ("/absolute", tarfile.REGTYPE), ("link", tarfile.SYMTYPE)],
)
def test_unsafe_archive_is_rejected_before_creating_destination(tmp_path, name, kind):
    folder = tmp_path / "archive"
    folder.mkdir()
    source = folder / "legacy-source.tar.gz"
    with tarfile.open(source, "w:gz") as out:
        member = tarfile.TarInfo(name)
        member.type = kind
        out.addfile(member, io.BytesIO(b""))
    (folder / "manifest.json").write_text(
        json.dumps({"archive_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "files": {}})
    )
    destination = tmp_path / "destination"
    with pytest.raises(ValueError, match="unsafe"):
        archive.extract(tmp_path, destination)
    assert not destination.exists()
