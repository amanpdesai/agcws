"""Reproducible legal random baseline for the AES transaction DSL."""
from __future__ import annotations

import random

from agcws.policies.base import SearchPolicy


class RandomSearch(SearchPolicy):
    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        generator = getattr(adapter, "random_workload", None)
        if generator is not None:
            return [generator(self.rng) for _ in range(n)]
        candidates = []
        minimum_blocks = max(16, int(getattr(adapter, "useful_work_floor", 16)))
        for _ in range(n):
            blocks = self.rng.randint(minimum_blocks, 64)
            candidates.append({"data_pattern": self.rng.randrange(4), "operations": [
                {"op": "configure", "key_len": self.rng.choice([128, 192, 256])},
                {"op": self.rng.choice(["encrypt", "decrypt"]), "blocks": blocks},
                {"op": "idle", "cycles": self.rng.randint(0, 200)},
            ]})
        return candidates
