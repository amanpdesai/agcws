"""Seeded baseline policy for temporal AES goals."""
from __future__ import annotations

import random

from agcws.policies.base import SearchPolicy


class TemporalRandomSearch(SearchPolicy):
    name = "temporal-random"

    def __init__(self, seed: int = 0, blocks: int = 38):
        self.rng = random.Random(seed)
        if blocks < 38:
            raise ValueError("temporal AES workloads require at least 38 blocks")
        self.blocks = blocks

    def propose(self, adapter, goal, history, n: int) -> list[dict]:
        candidates = []
        for _ in range(n):
            gaps = [self.rng.randrange(0, 101) for _ in range(self.blocks - 1)]
            operations = [{"op": "configure"}]
            for index in range(self.blocks):
                operations.append({"op": "encrypt", "blocks": 1})
                if index < len(gaps) and gaps[index]:
                    operations.append({"op": "idle", "cycles": gaps[index]})
            candidates.append({"data_pattern": self.rng.randrange(4), "operations": operations})
        return candidates
