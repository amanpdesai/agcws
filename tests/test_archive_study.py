import gzip

import pytest

from agcws.pipeline.storage import write
from maintenance.archive_study import pack, restore


def test_pack_round_trip_and_reject_overwrite(tmp_path):
    root, output, restored = (tmp_path / n for n in ("run", "pack", "restore"))
    write(root / "manifest.json", {"test": "fixture"})
    write(root / "complete.json", {"cells": 1})
    write(root / "panel/t/0/phase-ga/batches/001/trials.json", [{"slot": 1}])
    (root / "large.fst").write_bytes(b"waveform")
    result = pack(root, output)
    assert result["raw_scratch_unchanged"]
    assert len(list(output.iterdir())) == 2
    restore(output, restored)
    for path in restored.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (root / path.relative_to(restored)).read_bytes()
    assert not (restored / "large.fst").exists() and (root / "large.fst").exists()
    with pytest.raises(FileExistsError):
        restore(output, restored)
    with pytest.raises(FileExistsError):
        pack(root, output)


def test_pack_refuses_incomplete_run(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    with pytest.raises(ValueError, match="complete"):
        pack(root, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_corrupted_shard_is_rejected_before_raw_restore(tmp_path):
    root, output, restored = (tmp_path / n for n in ("run", "pack", "restore"))
    write(root / "manifest.json", {})
    write(root / "complete.json", {})
    pack(root, output)
    (output / "evidence-000.tar.gz").write_bytes(gzip.compress(b"corrupt"))
    with pytest.raises(ValueError, match="checksum"):
        restore(output, restored)
    assert not restored.exists()
