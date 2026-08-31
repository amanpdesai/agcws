from dataclasses import dataclass
from pathlib import Path
import hashlib
import json

@dataclass(frozen=True)
class TrialArtifacts:
    root: Path
    workload: Path
    provenance: Path
    activity: Path
    result: Path

def trial_artifacts(root: Path, trial_id: str, inputs: dict) -> TrialArtifacts:
    """Create/reopen an immutable, resumable artifact directory for a trial."""
    if not trial_id or "/" in trial_id or ".." in trial_id:
        raise ValueError("trial_id must be a simple path-safe identifier")
    directory = root / trial_id
    directory.mkdir(parents=True, exist_ok=True)
    workload = directory / "workload.json"
    provenance = directory / "provenance.json"
    activity = directory / "activity.json"
    result = directory / "result.json"
    if not workload.exists():
        workload.write_text(json.dumps(inputs, indent=2, sort_keys=True) + "\n")
    digest = hashlib.sha256(workload.read_bytes()).hexdigest()
    if not provenance.exists():
        provenance.write_text(json.dumps({"trial_id": trial_id, "workload_sha256": digest}, indent=2) + "\n")
    return TrialArtifacts(directory, workload, provenance, activity, result)
