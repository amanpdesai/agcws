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
    assert 'DMA_P_MIN' in text
    assert 'DMA_P_MAX' in text
    assert '--p-min "$(DMA_P_MIN)"' in text
    assert '--p-max "$(DMA_P_MAX)"' in text
    assert "infer-dma:" in text
    assert "DMA_INFERENCE_ROOTS" in text
    assert "DMA_CALIBRATION_ROOTS" in text
    assert "aggregate-temporal-pilot:" in text
    assert "aggregate-compositional-pilot:" in text
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


def test_makefile_loads_and_exports_host_environment_contract():
    text = Path("Makefile").read_text()
    assert "-include .env" in text
    assert "export AGCWS_SLANG_PLUGIN" in text
    assert "AGCWS_LIBERTY AGCWS_LIBERTY_NANGATE45" in text


def test_makefile_ibex_tasks_are_selectable_and_reproducible():
    text = Path("Makefile").read_text()
    assert "IBEX_CORE" in text
    assert "--core \"$(IBEX_CORE)\"" in text
    assert "IBEX_SOURCES" in text
    assert "$(if $(AGCWS_ARTIFACT_ROOT),$(AGCWS_ARTIFACT_ROOT),out)/ibex-sources/sources.json" in text
    assert "--top \"$(IBEX_TOP)\"" in text
    assert "verify-ibex: run-ibex" in text
    assert '"$${AGCWS_ARTIFACT_ROOT:-out}/ibex"' in text
    assert '"$${IBEX_ARTIFACT:-$${AGCWS_ARTIFACT_ROOT:-out}/ibex}"' in text
    assert "generate_ibex_workload.py" in text
    assert "lowrisc:ibex:ibex_core" in text


def test_synthesis_scripts_expose_opt_in_memory_mapping():
    for name in ("scripts/synthesize_aes_core.sh", "scripts/synthesize_axi_dma.sh"):
        text = Path(name).read_text()
        assert "AGCWS_MEMORY_LIBMAP" in text
        assert "memory_libmap -lib" in text
        assert "memory_libmap_sha256" in text
