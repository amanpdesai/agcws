from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class ScalarGoal:
    q: float
    tolerance: float = 0.05

@dataclass(frozen=True)
class CompositionalGoal:
    shares: dict[str, float]
    power_floor: float
    tolerance: float = 0.05

@dataclass(frozen=True)
class TemporalGoal:
    windows: int
    profile: list[float]
    tolerance: float = 0.10

Goal = Union[ScalarGoal, CompositionalGoal, TemporalGoal]
