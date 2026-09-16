import shutil
import subprocess

import pytest

from agcws.pipeline.retention import compact, finalize


@pytest.mark.skipif(not shutil.which("zstd"), reason="zstd required")
def test_lossless_retirement(tmp_path):
    waveform = tmp_path / "activity.vcd"
    data = b"$timescale 1ps $end\n#0\n" * 1000
    waveform.write_bytes(data)
    with pytest.raises(ValueError, match="checkpoint"):
        finalize(tmp_path, tmp_path / "result.json")
    assert waveform.exists()
    (tmp_path / "result.json").write_text('{"valid": true}')
    finalize(tmp_path, tmp_path / "result.json")
    assert not waveform.exists()
    assert subprocess.check_output(["zstd", "-qdc", str(tmp_path / "activity.vcd.zst")]) == data
    assert (tmp_path / "activity.vcd.retention.json").is_file()
    finalize(tmp_path, tmp_path / "result.json")
    from maintenance.restore_waveform import restore
    restored = tmp_path / "restored.vcd"
    restore(tmp_path / "activity.vcd.retention.json", restored)
    assert restored.read_bytes() == data
    with pytest.raises(FileExistsError):
        restore(tmp_path / "activity.vcd.retention.json", restored)


def test_reject_symlink(tmp_path):
    original = tmp_path / "original"
    original.write_text("trace")
    link = tmp_path / "activity.vcd"
    link.symlink_to(original)
    with pytest.raises(ValueError, match="nonsymlink"):
        compact(link)
    assert original.read_text() == "trace"


def test_bad_fst_preserves_vcd(tmp_path, monkeypatch):
    waveform = tmp_path / "activity.vcd"
    waveform.write_text("trace")
    (tmp_path / "activity.fst").write_text("wrong")
    monkeypatch.setattr("agcws.pipeline.retention.command_digest", lambda cmd: ("bad", 0))
    with pytest.raises(ValueError, match="exact VCD"):
        compact(waveform)
    assert waveform.exists()
