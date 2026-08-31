from pathlib import Path


def test_container_smoke_checks_frontend_and_both_liberties():
    text = Path("scripts/container_smoke.sh").read_text()
    assert "help read_slang" in text
    assert "AGCWS_LIBERTY_NANGATE45" in text


def test_docker_context_excludes_generated_artifacts():
    text = Path(".dockerignore").read_text()
    assert "out" in text
    assert "*.vcd" in text
    assert ".env" in text
