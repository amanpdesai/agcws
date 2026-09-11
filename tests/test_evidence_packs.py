import gzip
import hashlib
import io
import json
import tarfile

import pytest

from agcws.pipeline.evidence import PACK, materialize, sha, verify
from maintenance.pack_evidence import retire


def packed(tmp_path, members=None):
    study = tmp_path / "results/example"
    study.mkdir(parents=True)
    data = b"actual output\n\x00\xff"
    name = "evaluations/key/run/ibex_simple_system.log.gz"
    files = {name: {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "mode": 0o644}}
    shard = study / "evidence-000.tar.gz"
    with tarfile.open(shard, "w:gz") as archive:
        for member_name, kind in members or [(name, tarfile.REGTYPE)]:
            member = tarfile.TarInfo(member_name)
            member.type = kind
            member.size = len(data) if kind == tarfile.REGTYPE else 0
            member.mode = 0o644
            archive.addfile(member, io.BytesIO(data))
    metadata = {"version": 1, "files": files, "shards": {shard.name: sha(shard)}}
    (study / PACK).write_bytes(gzip.compress(json.dumps(metadata).encode()))
    (study / "manifest.json").write_text('{"frozen":true}\n')
    return study, name, data


def test_lossless_restoration_and_review_view(tmp_path):
    repo = tmp_path / "repo"
    study, name, data = packed(repo)
    (repo / "docs").mkdir()
    (repo / "docs/PLAN.md").write_text("plan")
    assert verify(study)["files"] == 1
    view = materialize(repo, tmp_path / "view", ["example"])
    assert (view / "results/example" / name).read_bytes() == data
    assert (view / "results/example/manifest.json").read_bytes() == b'{"frozen":true}\n'
    assert (view / "docs/PLAN.md").read_text() == "plan"
    with pytest.raises(FileExistsError):
        materialize(repo, view, ["example"])


@pytest.mark.parametrize(
    "name,kind",
    [
        ("../escape", tarfile.REGTYPE),
        ("/absolute", tarfile.REGTYPE),
        ("link", tarfile.SYMTYPE),
        ("unlisted", tarfile.REGTYPE),
    ],
)
def test_reject_unsafe_or_unlisted_members(tmp_path, name, kind):
    study, _, _ = packed(tmp_path, [(name, kind)])
    with pytest.raises(ValueError):
        verify(study, tmp_path / "restored")
    assert not (tmp_path / "escape").exists()


def test_reject_shard_corruption_before_extraction(tmp_path):
    study, _, _ = packed(tmp_path)
    (study / "evidence-000.tar.gz").write_bytes(b"bad")
    with pytest.raises(ValueError, match="checksum"):
        verify(study, tmp_path / "restored")
    assert not (tmp_path / "restored").exists()


def test_reject_duplicate_members(tmp_path):
    name = "evaluations/key/run/ibex_simple_system.log.gz"
    study, _, _ = packed(tmp_path, [(name, tarfile.REGTYPE)] * 2)
    with pytest.raises(ValueError, match="duplicate"):
        verify(study)


def test_unknown_study_does_not_create_view(tmp_path):
    repo = tmp_path / "repo"
    packed(repo)
    with pytest.raises(ValueError, match="existing"):
        materialize(repo, tmp_path / "view", ["../unknown"])
    assert not (tmp_path / "view").exists()


def test_retirement_rejects_modified_loose_file(tmp_path):
    study, name, _ = packed(tmp_path)
    path = study / name
    path.parent.mkdir(parents=True)
    path.write_bytes(b"user edit")
    with pytest.raises(ValueError, match="changed"):
        retire(tmp_path, "example")
    assert path.read_bytes() == b"user edit"


def test_retirement_deletes_only_verified_loose_copy(tmp_path):
    study, name, data = packed(tmp_path)
    path = study / name
    path.parent.mkdir(parents=True)
    path.write_bytes(data)
    unrelated = study / "untracked.txt"
    unrelated.write_text("keep")
    retire(tmp_path, "example")
    assert not path.exists()
    assert unrelated.read_text() == "keep"
    assert verify(study)["files"] == 1
