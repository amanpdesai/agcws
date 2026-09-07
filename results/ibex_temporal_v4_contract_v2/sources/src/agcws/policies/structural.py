"""Shared-representation random and population-based temporal baselines."""
import random

from agcws.policies.base import SearchPolicy
from agcws.policies.structural_population import temporal_population
from agcws.workloads.schedule import random_schedule
from agcws.workloads.structural_edits import random_structural_edit


class StructuralRandom(SearchPolicy):
    name = 'structural-random-v1'

    def __init__(self, seed):
        self.rng = random.Random(seed)

    def propose(self, adapter, goal, history, n):
        return [random_schedule(self.rng, adapter.contract) for _ in range(n)]


class StructuralEvolution(StructuralRandom):
    name = 'structural-evolution-v1'

    def select_parents(self, history):
        return sorted((t for t in history if t.validity.valid and t.loss is not None),
                      key=lambda t: t.loss)[:8]

    def propose(self, adapter, goal, history, n):
        parents = self.select_parents(history)
        if not parents:
            return super().propose(adapter, goal, history, n)
        return [random_schedule(self.rng, adapter.contract) if self.rng.random() < 0.2
                else random_structural_edit(self.rng.choice(parents).workload, adapter.contract, self.rng)
                for _ in range(n)]


class StructuralPopulationEvolution(StructuralEvolution):
    name = 'structural-population-evolution-v1'

    def select_parents(self, history):
        return temporal_population(history)
