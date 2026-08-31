from pathlib import Path


def test_makefile_exposes_core_tasks():
    text = Path("Makefile").read_text()
    for target in ("test:", "synth-aes:", "evaluate-aes:", "verify:", "container-smoke:"):
        assert target in text


def test_makefile_exposes_baseline_matrix_task():
    text = Path("Makefile").read_text()
    assert "baseline-matrix:" in text
    assert "AGCWS_SEARCH_TARGETS" in text
    assert "$(P_MIN)" in text
    assert "$(P_MAX)" in text
