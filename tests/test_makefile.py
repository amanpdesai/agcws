from pathlib import Path


def test_makefile_exposes_core_tasks():
    text = Path("Makefile").read_text()
    for target in ("test:", "synth-aes:", "evaluate-aes:", "verify:", "verify-ibex:", "probe-ibex-synthesis:", "chia-node-smoke:", "audit-reproducibility:", "vertex-preflight:", "container-smoke:"):
        assert target in text
    assert "verify:" in text
    verify_body = text.split("verify:", 1)[1]
    assert "audit-reproducibility" in verify_body
    assert "verify-artifact" in verify_body
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


def test_makefile_exposes_dual_pdk_liberty_inspection():
    text = Path("Makefile").read_text()
    assert "inspect-liberties:" in text
    target = text.split("inspect-liberties:", 1)[1].split("\n", 3)
    body = "\n".join(target)
    assert "AGCWS_LIBERTY" in body
    assert "AGCWS_LIBERTY_NANGATE45" in body


def test_makefile_ibex_tasks_are_selectable_and_reproducible():
    text = Path("Makefile").read_text()
    assert "IBEX_CORE" in text
    assert "--core \"$(IBEX_CORE)\"" in text
    assert "IBEX_SOURCES" in text
    assert "--top \"$(IBEX_TOP)\"" in text
