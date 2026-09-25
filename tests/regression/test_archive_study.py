import gzip
import random

import pytest

from agcws.core.storage import write
from agcws.evidence.study_archive import pack, restore, shard_groups


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


def test_multiple_bounded_shards_restore_every_byte(tmp_path):
    root, output, restored = (tmp_path / name for name in ("run", "pack", "restored"))
    write(root / "manifest.json", {})
    write(root / "complete.json", {})
    rng = random.Random(1)
    for index in range(4):
        write(root / f"panel/{index}/trials.json", {"data": rng.randbytes(50000).hex()})
    pack(root, output, max_shard_bytes=128*1024)
    shards = list(output.glob("evidence-*.tar.gz"))
    assert len(shards) > 1 and all(p.stat().st_size <= 128*1024 for p in shards)
    restore(output, restored)
    for path in root.rglob("*.json"):
        assert path.read_bytes() == (restored / path.relative_to(root)).read_bytes()


def test_oversized_member_is_not_silently_written(tmp_path):
    path = tmp_path / "large"
    path.write_bytes(b"x" * 70000)
    with pytest.raises(ValueError, match="individual evidence member"):
        shard_groups([path], 128*1024)


def test_streaming_export_matches_common_export_selection(tmp_path):
    from agcws.studies.engine import export

    root, output, restored, ordinary = (tmp_path/n for n in ('run', 'pack', 'restored', 'ordinary'))
    write(root/'manifest.json', {})
    write(root/'complete.json', {})
    write(root/'cache/abc/result.json', {'valid': True})
    write(root/'panel/t/1/phase-ga/complete.json', {'solved': False})
    write(root/'toolchain/build.json', {'exclude': True})
    (root/'cache/abc/trace_core_00000000.log').write_text('excluded trace')
    (root/'cache/abc/driver.log').write_text('retained log')
    export(root, ordinary)
    pack(root, output)
    restore(output, restored)
    import json

    expected = json.loads((ordinary/'inventory.json').read_text())
    assert set(expected) == {str(p.relative_to(restored)) for p in restored.rglob('*') if p.is_file()}


def test_changed_source_after_pack_fails_verification(tmp_path, monkeypatch):
    from agcws.evidence import packs as evidence

    root = tmp_path/'run'
    write(root/'manifest.json', {})
    write(root/'complete.json', {})
    original = evidence.verify

    def tamper(*args, **kwargs):
        result = original(*args, **kwargs)
        (root/'complete.json').write_text('{"changed": true}')
        return result

    monkeypatch.setattr(evidence, 'verify', tamper)
    with pytest.raises(ValueError, match='restored raw bytes differ'):
        pack(root, tmp_path/'archive')
