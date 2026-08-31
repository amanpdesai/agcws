from pathlib import Path


def test_makefile_exposes_core_tasks():
    text = Path("Makefile").read_text()
    for target in ("test:", "synth-aes:", "evaluate-aes:", "verify:", "container-smoke:"):
        assert target in text
