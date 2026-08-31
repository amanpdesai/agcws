from pathlib import Path

from agcws.provenance import file_sha256, input_record


def test_input_record_contains_streamed_digest(tmp_path: Path):
    path = tmp_path / "input.bin"
    path.write_bytes(b"agcws")
    record = input_record({"input": path})["input"]
    assert record["bytes"] == 5
    assert record["sha256"] == file_sha256(path)
