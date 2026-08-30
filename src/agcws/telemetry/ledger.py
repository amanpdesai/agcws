from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass
class Trial:
    trial_id: str
    design: str
    goal: Any
    policy: str
    seed: int
    workload: dict
    validity: Any
    profile: Any = None
    wall_clock_s: float = 0.0
    sim_count: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = ""
    est_cost_usd: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
