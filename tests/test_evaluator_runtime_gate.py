from pathlib import Path


def test_evaluator_composes_runtime_useful_work_gate():
    text = Path("scripts/evaluate_aes_workload.py").read_text()
    assert "validate_result" in text
    assert "SimResult" in text
    assert "allow_invalid" in text
