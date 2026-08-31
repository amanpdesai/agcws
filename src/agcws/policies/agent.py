"""Batched agent policy boundary.

The runner owns fairness and evaluation budgets. This module owns only the
proposal boundary, making the LLM provider replaceable and testable offline.
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from agcws.policies.base import SearchPolicy
from agcws.policies.prompt import prompt_hash


class AgentPolicy(SearchPolicy):
    name = "agent"

    def __init__(self, proposer: Callable[[Any, Any, list[Any], int], list[dict]], *,
                 model: str = "offline", prompt_hash: str = ""):
        self.proposer = proposer
        self.model = model
        self.prompt_hash = prompt_hash

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        if n <= 0:
            return []
        candidates = self.proposer(adapter, goal, history, n)
        if not isinstance(candidates, list):
            raise TypeError("agent proposer must return a list")
        return candidates[:n]


class OfflineAgent(AgentPolicy):
    """Deterministic semantic proposer used for smoke tests and dry runs."""

    def __init__(self, seed: int = 0):
        import random
        rng = random.Random(seed)

        def propose(adapter, goal, history, n):
            generator = getattr(adapter, "random_workload", None)
            if generator is not None:
                return [generator(rng) for _ in range(n)]
            candidates = []
            minimum_blocks = max(16, int(getattr(adapter, "useful_work_floor", 16)))
            for _ in range(n):
                blocks = minimum_blocks + rng.randrange(17)
                candidates.append({"data_pattern": rng.randrange(4), "operations": [
                    {"op": "configure", "key_len": 128},
                    {"op": "encrypt", "blocks": blocks},
                ]})
            return candidates

        prompt = Path(__file__).resolve().parents[3] / "prompts/agent_system_v1.txt"
        super().__init__(propose, model="offline-deterministic",
                         prompt_hash=prompt_hash(prompt))


class OneShotAgent(OfflineAgent):
    """Reuse one deterministic proposal batch without observing history."""

    name = "one-shot-agent"

    def __init__(self, seed: int = 0):
        super().__init__(seed)
        self._batch: list[dict] | None = None

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        if self._batch is None:
            self._batch = super().propose(adapter, goal, [], max(n, 8))
        return [self._batch[index % len(self._batch)] for index in range(n)]
