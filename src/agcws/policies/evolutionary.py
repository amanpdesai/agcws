"""Small budget-neutral evolutionary policy over workload dictionaries."""
from __future__ import annotations

import random

from agcws.policies.base import SearchPolicy
from agcws.policies.mutation import MutationSearch
from agcws.policies.random_search import RandomSearch


class EvolutionarySearch(SearchPolicy):
    name = "evolutionary"

    def __init__(self, seed: int = 0, elite_size: int = 4):
        self.rng = random.Random(seed)
        self.elite_size = elite_size
        self.mutator = MutationSearch(seed + 1)

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        scored = [trial for trial in history if trial.profile is not None and trial.validity.valid]
        scored.sort(key=lambda trial: getattr(trial, "loss", float("inf")))
        if not scored:
            return RandomSearch(self.rng.randrange(2**31)).propose(adapter, goal, history, n)
        elites = [trial.workload for trial in scored[:self.elite_size]]
        return [self.mutator._mutate(self.rng.choice(elites)) for _ in range(n)]
