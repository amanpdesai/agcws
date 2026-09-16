import hashlib
import json
import tarfile

import pytest

from maintenance import retire_baseline_panel as retirement


def test_archive_interrupted_panel_preserves_evidence_and_excludes_waves(tmp_path, monkeypatch):
    monkeypatch.setattr(retirement, "ROOT", tmp_path)
    monkeypatch.setattr(retirement, "PANEL", tmp_path / "out/panel")
    root = retirement.PANEL / "ibex"
    root.mkdir(parents=True)
    (root / "manifest.json").write_text('{"frozen": true}')
    (root / "activity.vcd").write_bytes(b"large waveform")
    (root / "run.log").write_text("diagnostic")
    retirement.archive("ibex")
    receipt = json.loads((tmp_path / "out/retired-baselines-maxbin-v1/ibex.json").read_text())
    assert receipt["panel_complete"] is False
    assert receipt["completed_cells"] == 0
    assert set(receipt["files"]) == {"manifest.json", "run.log"}
    with tarfile.open(tmp_path / "out/retired-baselines-maxbin-v1/ibex.tar.gz") as archive:
        for member in archive:
            assert hashlib.sha256(archive.extractfile(member).read()).hexdigest() == receipt["files"][member.name]
    assert (root / "activity.vcd").read_bytes() == b"large waveform"


def test_archive_rejects_symlink_without_deletion(tmp_path, monkeypatch):
    monkeypatch.setattr(retirement, "ROOT", tmp_path)
    monkeypatch.setattr(retirement, "PANEL", tmp_path / "out/panel")
    root = retirement.PANEL / "aes"
    root.mkdir(parents=True)
    (root / "outside.json").symlink_to(tmp_path / "absent")
    with pytest.raises(ValueError, match="symlink"):
        retirement.archive("aes")
    assert (root / "outside.json").is_symlink()


def test_resume_checks_retained_bytes(tmp_path):
    vcd = tmp_path / "activity.vcd"
    vcd.write_text("exact waveform\n")
    receipt = retirement.retire_or_verify(vcd)
    assert not vcd.exists()
    assert retirement.retire_or_verify(vcd) == receipt
    (tmp_path / receipt["retained"]).write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="changed"):
        retirement.retire_or_verify(vcd)
