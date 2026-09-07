import json

import pytest

from maintenance.trace_store import digest, pack_file, restore, verify_object


def test_verified_deduplicated_round_trip(tmp_path):
    source = tmp_path / "source.vcd"
    source.write_bytes(b"known transitions\n" * 1000)
    objects = tmp_path / "objects"
    first = pack_file(source, objects)
    second = pack_file(source, objects)
    assert first == second
    verify_object(first)
    assert first["compressed_bytes"] < first["raw_bytes"]
    index = tmp_path / "index.json"
    index.write_text(json.dumps({"entries": [{"path": "source.vcd", **first}]}))
    restored = tmp_path / "restored.vcd"
    restore(index, "source.vcd", restored)
    assert restored.read_bytes() == source.read_bytes()
    assert digest(restored) == first["sha256"]
    restored.write_text("different")
    with pytest.raises(ValueError, match="overwrite"):
        restore(index, "source.vcd", restored)


def test_corrupt_object_rejected(tmp_path):
    source = tmp_path / "source.vcd"
    source.write_text("some waveform")
    entry = pack_file(source, tmp_path / "objects")
    from pathlib import Path

    Path(entry["object"]).write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="changed"):
        verify_object(entry)
