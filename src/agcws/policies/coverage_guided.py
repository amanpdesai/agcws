"""Queue-based mutation guided by newly reached instrumented DUT blocks."""
import random

from agcws.policies.base import SearchPolicy
from agcws.policies.mutation import MutationSearch
from agcws.policies.random_search import RandomSearch


class CoverageGuidedSearch(SearchPolicy):
    name = 'coverage-guided-line'

    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.random = RandomSearch(seed)
        self.mutator = MutationSearch(seed)

    def propose(self, adapter, goal, history, n):
        queue, reached = [], set()
        for trial in history:
            if not trial.validity.valid or trial.profile is None:
                continue
            provenance = trial.profile.provenance or {}
            if 'coverage_hits' not in provenance:
                raise ValueError('coverage-guided policy requires instrumented DUT coverage')
            hits = set(provenance['coverage_hits'])
            if not queue or hits - reached:
                queue.append(trial.workload)
            reached.update(hits)
        if not queue:
            return self.random.propose(adapter, goal, history, n)
        return [self.random.propose(adapter, goal, history, 1)[0] if self.rng.random() < 0.2
                else self.mutator._mutate(self.rng.choice(queue), adapter) for _ in range(n)]
