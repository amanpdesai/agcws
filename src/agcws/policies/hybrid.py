"""Agent-guided evolutionary policy with a common proposal interface."""
from __future__ import annotations

from agcws.policies.agent import AgentPolicy
from agcws.policies.mutation import MutationSearch


class HybridSearch(AgentPolicy):
    name = "hybrid"

    def __init__(self, proposer, seed: int = 0, agent_fraction: float = 0.5,
                 model: str = "offline", prompt_hash: str = ""):
        if not 0.0 <= agent_fraction <= 1.0:
            raise ValueError("agent_fraction must be in [0,1]")
        super().__init__(proposer, model=model, prompt_hash=prompt_hash)
        self.agent_fraction = agent_fraction
        self.mutator = MutationSearch(seed)

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        agent_count = round(n * self.agent_fraction)
        proposals = super().propose(adapter, goal, history, agent_count)
        remaining = n - len(proposals)
        if remaining:
            proposals.extend(self.mutator.propose(adapter, goal, history, remaining))
        return proposals[:n]
