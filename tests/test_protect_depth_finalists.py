import json

import pytest

from maintenance import protect_depth_finalists as protection
from maintenance.clean_artifacts import fingerprint


def test_filter_keeps_finalist_and_does_not_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(protection, "REPO", tmp_path)
    monkeypatch.setattr(protection, "protected_ids", lambda _: {"keep"})
    entries = []
    for identifier in ("keep", "old"):
        p = tmp_path / "out" / "ibex-depth-v1" / "cache" / identifier / "trace.fst"
        p.parent.mkdir(parents=True)
        p.write_bytes(b"waveform")
        entries.append(
            {
                "path": str(p.relative_to(tmp_path / "out")),
                "fingerprint": fingerprint(p),
            }
        )
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "root": str(tmp_path / "out"),
                "targets": ["ibex-depth-v1"],
                "files": entries,
            }
        )
    )
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "sha256.json").write_text("{}")
    output = tmp_path / "filtered.json"
    protection.filter_plan(plan, archive, output)
    filtered = json.loads(output.read_text())
    assert filtered["files"] == [entries[1]]
    assert filtered["retained_finalist_files"] == 1
    assert all((tmp_path / "out" / e["path"]).exists() for e in entries)


def test_filter_rejects_other_root(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"root": "/", "targets": ["ibex-depth-v1"]}))
    with pytest.raises(ValueError):
        protection.filter_plan(plan, tmp_path, tmp_path / "out.json")
