from dataclasses import dataclass, field
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
    loss: float | None = None
    wall_clock_s: float = 0.0
    sim_count: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = ""
    prompt_hash: str = ""
    claim_scope: str = "baseline"
    est_cost_usd: float = 0.0
    timestamp: str = ""
    generation_wall_clock_s: float = 0.0
    generation_diagnostics: dict = field(default_factory=dict)
    evaluation_attempts: int = 0
    evaluation_diagnostics: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
