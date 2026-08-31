from pathlib import Path

from scripts.audit_reproducibility import audit


def test_audit_reports_repository_inputs():
    result = audit(Path.cwd())
    assert result["valid"]
    assert result["chia_commit"]
    assert result["prompt_sha256"]
    assert not result["missing"]


def test_audit_reports_missing_input(tmp_path: Path):
    result = audit(tmp_path)
    assert not result["valid"]
    assert ".env.example" in result["missing"]
