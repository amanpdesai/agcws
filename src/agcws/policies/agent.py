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
    claim_scope = "cross_design_agent"

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

    claim_scope = "heuristic_smoke_only"

    def __init__(self, seed: int = 0):
        import random
        rng = random.Random(seed)

        def propose(adapter, goal, history, n):
            if hasattr(adapter, "random_workload") and hasattr(goal, "q"):
                import copy
                q = max(0.0, min(1.0, float(goal.q)))
                candidates = []
                seen = {repr(getattr(item, "workload", item)) for item in history}
                for _ in range(n * 4):
                    candidate = adapter.random_workload(rng)
                    ops = candidate.get("operations", [])
                    crypto = [op for op in ops if op.get("op") in {"encrypt", "decrypt"}]
                    if not crypto:
                        continue
                    if crypto:
                        desired = max(1, int(adapter.useful_work_floor + q * (256 - adapter.useful_work_floor)))
                        desired = max(adapter.useful_work_floor,
                                     min(256, desired + rng.randint(-8, 8)))
                        crypto[0]["blocks"] = desired - sum(op.get("blocks", 0) for op in crypto[1:])
                        if crypto[0]["blocks"] <= 0:
                            continue
                    key = repr(candidate)
                    if key not in seen:
                        seen.add(key)
                        candidates.append(copy.deepcopy(candidate))
                    if len(candidates) == n:
                        return candidates
            generator = getattr(adapter, "random_workload", None)
            if generator is not None:
                mutator = getattr(adapter, "mutate_workload", None)
                candidates = []
                for _ in range(n):
                    candidate = generator(rng)
                    if mutator is not None:
                        original = repr(candidate)
                        for _attempt in range(4):
                            candidate = mutator(candidate, rng)
                            if repr(candidate) != original:
                                break
                    candidates.append(candidate)
                return candidates
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
