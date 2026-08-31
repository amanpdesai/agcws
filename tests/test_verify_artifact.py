import hashlib
import json
from pathlib import Path

import pytest

from scripts.verify_artifact import verify


def _artifact(tmp_path: Path) -> Path:
    artifact = tmp_path / "evaluation"
    artifact.mkdir()
    payload = artifact / "activity.json"
    payload.write_text('{"clock_edges": 1}\n')
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


def test_verify_artifact_rejects_inconsistent_normalized_activity(tmp_path: Path):
    artifact = _artifact(tmp_path)
    payload = artifact / "activity.json"
    payload.write_text(json.dumps({
        "per_cycle_toggles": [1, 2], "window_toggles": [1, 2],
        "normalized_windows": [1.0, 1.0], "waveform_sha256": "0" * 64,
    }) + "\n")
    result = json.loads((artifact / "result.json").read_text())
    activity_record = result["provenance"]["inputs"]["activity"]
    activity_record["sha256"] = hashlib.sha256(payload.read_bytes()).hexdigest()
    activity_record["bytes"] = payload.stat().st_size
    (artifact / "result.json").write_text(json.dumps(result))
    with pytest.raises(ValueError, match="normalized profile"):
        verify(artifact)
