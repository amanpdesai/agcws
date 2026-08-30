from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class PowerProfile:
    mean_power: float
    peak_power: float
    windowed: list[float] | None = None
    by_region: dict[str, float] | None = None
    useful_work: float = 0.0
    valid: bool = False
    fidelity: Literal["activity", "synthesis"] = "activity"
    provenance: dict[str, str] | None = None

def target_error(profile: PowerProfile, target: float) -> float:
    """Scalar normalized error; goal-specific losses belong in goals/loss.py."""
    return abs(profile.mean_power - target)
