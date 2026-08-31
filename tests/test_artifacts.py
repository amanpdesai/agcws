from pathlib import Path
import pytest
from agcws.nodes.activity import windowize
from agcws.nodes.artifacts import trial_artifacts

def test_windowize_is_deterministic():
    assert windowize([1, 2, 3, 4], 2) == (3, 7)

def test_trial_artifacts_are_resumable(tmp_path: Path):
    first = trial_artifacts(tmp_path, "trial-1", {"operations": []})
    second = trial_artifacts(tmp_path, "trial-1", {"operations": []})
    assert first.workload.read_text() == second.workload.read_text()
    assert first.provenance.exists()


def test_trial_artifacts_reject_input_reuse_with_different_workload(tmp_path: Path):
    trial_artifacts(tmp_path, "trial-1", {"operations": []})
    with pytest.raises(ValueError, match="different inputs"):
        trial_artifacts(tmp_path, "trial-1", {"operations": ["encrypt"]})
