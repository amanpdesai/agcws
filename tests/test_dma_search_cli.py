from pathlib import Path


def test_dma_search_exposes_explicit_policy_matrix_mode():
    text = Path("scripts/run_axi_dma_search.py").read_text()
    assert "--policies" in text
    assert "matrix.json" in text
