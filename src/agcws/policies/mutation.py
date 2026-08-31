"""Generic workload mutation baseline shared across design adapters."""
from __future__ import annotations

import copy
import random

from agcws.policies.base import SearchPolicy


class MutationSearch(SearchPolicy):
    name = "mutation"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        parents = [trial.workload for trial in history if getattr(trial, "validity", None)
                   and trial.validity.valid and trial.workload]
        if not parents:
            from agcws.policies.random_search import RandomSearch
            return RandomSearch(self.rng.randrange(2**31)).propose(adapter, goal, history, n)
        return [self._mutate(self.rng.choice(parents), adapter) for _ in range(n)]

    def _mutate(self, workload: dict, adapter=None) -> dict:
        custom = getattr(adapter, "mutate_workload", None)
        if custom is not None:
            return custom(workload, self.rng)
        candidate = copy.deepcopy(workload)
        operations = candidate.get("operations", [])
        crypto = [op for op in operations if op.get("op") in {"encrypt", "decrypt"}]
        choice = self.rng.randrange(3)
        if choice == 0 and crypto:
            op = self.rng.choice(crypto)
            op["blocks"] = max(1, min(256, int(op.get("blocks", 1)) + self.rng.randint(-8, 8)))
        elif choice == 1:
            candidate["data_pattern"] = self.rng.randrange(4)
        elif choice == 2:
            idle = next((op for op in operations if op.get("op") == "idle"), None)
            if idle is None:
                operations.append({"op": "idle", "cycles": self.rng.randrange(201)})
            else:
                idle["cycles"] = self.rng.randrange(201)
        return candidate
