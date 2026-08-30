from dataclasses import dataclass
from pathlib import Path
from agcws.nodes.commands import CommandResult, run_command

@dataclass(frozen=True)
class ActivityArtifact:
    activity_file: Path
    annotation_fraction: float | None = None

def extract_activity(command: list[str], waveform: Path, output_dir: Path) -> tuple[CommandResult, ActivityArtifact]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(command, cwd=output_dir)
    return result, ActivityArtifact(output_dir / "activity.saif")
