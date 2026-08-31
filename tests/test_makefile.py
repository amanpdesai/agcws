from pathlib import Path


def test_makefile_exposes_core_tasks():
    text = Path("Makefile").read_text()
    for target in ("test:", "synth-aes:", "evaluate-aes:", "verify:", "container-smoke:"):
        assert target in text
    assert "DMA_POLICIES" in text
    assert 'DMA_SEARCH_DIR' in text
    assert '--budget "$(BUDGET)"' in text
    assert "plot-search-curves:" in text


def test_makefile_exposes_baseline_matrix_task():
    text = Path("Makefile").read_text()
    assert "baseline-matrix:" in text
    assert "AGCWS_SEARCH_TARGETS" in text
    assert "$(P_MIN)" in text
    assert "$(P_MAX)" in text
    assert "AGCWS_PYTHON=$(VENV_PYTHON)" in text


def test_makefile_exposes_explicit_chia_install():
    text = Path("Makefile").read_text()
    assert "chia-install:" in text
    assert "pip install -e tools/chia" in text
