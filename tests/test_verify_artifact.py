import json
from pathlib import Path

import pytest

from scripts.verify_artifact import verify


def _artifact(tmp_path: Path) -> Path:
    artifact = tmp_path / "evaluation"
    artifact.mkdir()
    payload = artifact / "activity.json"
    payload.write_text('{"clock_edges": 1}\n')
    import hashlib
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    (artifact / "result.json").write_text(json.dumps({
        "valid": True,
        "useful_work": 16,
        "provenance": {"inputs": {
            "activity": {"path": "activity.json", "bytes": payload.stat().st_size,
                          "sha256": digest}
        }},
    }))
    return artifact


def test_verify_artifact_checks_input_hashes(tmp_path: Path):
    assert verify(_artifact(tmp_path))["inputs_checked"] == 1


def test_verify_artifact_rejects_changed_input(tmp_path: Path):
    artifact = _artifact(tmp_path)
    (artifact / "activity.json").write_text("changed\n")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        verify(artifact)
