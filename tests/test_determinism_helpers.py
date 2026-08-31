from pathlib import Path

from scripts.check_aes_determinism import digest


def test_digest_is_content_based(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.write_text("same")
    second.write_text("same")
    assert digest(first) == digest(second)
