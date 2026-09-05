"""Versioned semantic mutation with a common random initialization."""
import json

from agcws.policies.random_search import RandomSearch
from agcws.policies.vertex import VertexAgent, _jsonable


class SemanticEvolution(VertexAgent):
    name = "semantic-evolution-v2"
    proposal_attempts = 1

    def initialize(self, seed, p_min, p_max):
        self.initializer = RandomSearch(seed)
        self.envelope = (p_min, p_max)
        return self

    def propose(self, adapter, goal, history, n):
        if not history:
            self.last_usage = {"tokens_in": 0, "tokens_out": 0}
            return self.initializer.propose(adapter, goal, history, n)
        return super().propose(adapter, goal, history, n)

    def build_payload(self, adapter, goal, history, n, system_prompt):
        lo, hi = self.envelope
        valid = [t for t in history if t.validity.valid and t.loss is not None]
        parents = sorted(valid, key=lambda t: t.loss)[:4]
        selected = parents + [t for t in history[-8:] if t not in parents]
        feedback = []
        for trial in selected:
            achieved = None
            if trial.validity.valid and trial.profile is not None:
                q = (trial.profile.mean_power - lo) / (hi - lo)
                achieved = {"q": q, "signed_residual": q - goal.q,
                            "activity": trial.profile.mean_power,
                            "useful_work": trial.profile.useful_work}
            feedback.append({"workload": trial.workload, "achieved": achieved,
                             "validity": _jsonable(trial.validity)})
        return json.dumps({
            "system_prompt": system_prompt,
            "design": {"name": adapter.name, "summary": adapter.design_summary,
                       "schema": adapter.workload_schema,
                       "constraints": adapter.protocol_constraints,
                       "minimum_useful_work": adapter.useful_work_floor},
            "goal": _jsonable(goal),
            "envelope": {"p_min": lo, "p_max": hi},
            "parents_and_recent_feedback": feedback,
            "batch_size": n,
        }, sort_keys=True)
