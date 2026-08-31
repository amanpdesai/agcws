from pathlib import Path


def test_baseline_matrix_uses_common_activity_runner():
    text = Path("scripts/run_aes_baseline_matrix.sh").read_text()
    for policy in ("random", "mutation", "evolutionary", "offline-hybrid"):
        assert policy in text
    assert "--fidelity activity" in text
    assert "aggregate_runs.py" in text
