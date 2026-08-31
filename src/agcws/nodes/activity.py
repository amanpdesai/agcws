from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence
from agcws.nodes.commands import CommandResult, run_command

@dataclass(frozen=True)
class ActivityArtifact:
    activity_file: Path
    annotation_fraction: float | None = None
    per_cycle_toggles: tuple[int, ...] = ()
    window_toggles: tuple[int, ...] = ()

def windowize(values: Sequence[int], windows: int) -> tuple[int, ...]:
    """Aggregate per-cycle toggles into deterministic coarse windows."""
    if windows <= 0 or not values:
        raise ValueError("windows must be positive and values must be non-empty")
    buckets = [0] * min(windows, len(values))
    for index, value in enumerate(values):
        buckets[index * len(buckets) // len(values)] += value
    return tuple(buckets)

def extract_activity(command: list[str], waveform: Path, output_dir: Path) -> tuple[CommandResult, ActivityArtifact]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(command, cwd=output_dir)
    return result, ActivityArtifact(output_dir / "activity.saif")
