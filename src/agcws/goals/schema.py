import math
from dataclasses import dataclass


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


@dataclass(frozen=True, kw_only=True)
class FixedTemporalGoal:
    windows: int
    profile: list[float]
    scale: float
    observation_cycles: int
    tolerance: float = 0.10
    loss_version: str = 'fixed-rate-capped-nrmse-v1'

    def __post_init__(self):
        if (type(self.windows) is not int or self.windows <= 0
                or len(self.profile) != self.windows
                or any(not math.isfinite(x) or x < 0 for x in self.profile)
                or not math.isfinite(self.scale) or self.scale <= 0
                or type(self.observation_cycles) is not int or self.observation_cycles < self.windows
                or not math.isfinite(self.tolerance) or not 0 <= self.tolerance < 1
                or self.loss_version != 'fixed-rate-capped-nrmse-v1'):
            raise ValueError('invalid fixed-window temporal goal')

Goal = ScalarGoal | CompositionalGoal | TemporalGoal | FixedTemporalGoal
