"""Generic complete-schedule agent and alternating agent/evolution hybrid."""
import json
from dataclasses import asdict

from agcws.policies.structural import StructuralEvolution, StructuralRandom
from agcws.policies.vertex import VertexAgent


class StructuralAgent(VertexAgent):
    name = 'structural-agent-v1'
    proposal_attempts = 1
    max_output_tokens = 8192
    thinking_budget = 512

    def initialize(self, seed):
        self.initializer = StructuralRandom(seed)
        self.evolution = StructuralEvolution(seed)
        self.batches = 0
        return self

    def propose(self, adapter, goal, history, n):
        self.batches += 1
        if not history:
            self.last_usage = {'tokens_in': 0, 'tokens_out': 0}
            self.last_diagnostics = {'proposal_source': 'shared_random_initialization'}
            return self.initializer.propose(adapter, goal, history, n)
        return super().propose(adapter, goal, history, n)

    def build_payload(self, adapter, goal, history, n, system_prompt):
        parents = sorted((t for t in history if t.validity.valid and t.loss is not None),
                         key=lambda t: t.loss)[:4]
        recent = [t for t in history[-8:] if t not in parents]
        feedback = []
        for trial in parents + recent:
            rates = trial.profile.windowed if trial.validity.valid and trial.profile else None
            feedback.append({'schedule': trial.workload, 'loss': trial.loss,
                             'observed_rates': rates,
                             'signed_residual': [(a - b) / goal.scale for a, b in zip(rates, goal.profile)] if rates else None,
                             'valid': trial.validity.valid, 'rejection': trial.validity.reason})
        return json.dumps({'system_prompt': system_prompt,
                           'design': {'name': adapter.name, 'summary': adapter.design_summary},
                           'schema': adapter.workload_schema, 'contract': asdict(adapter.contract),
                           'constraints': adapter.protocol_constraints,
                           'goal': asdict(goal), 'history': feedback, 'batch_size': n}, sort_keys=True)


class StructuralHybrid(StructuralAgent):
    name = 'structural-hybrid-v1'

    def propose(self, adapter, goal, history, n):
        if history and self.batches % 2 == 0:
            self.batches += 1
            self.last_usage = {'tokens_in': 0, 'tokens_out': 0}
            self.last_diagnostics = {'proposal_source': 'structural_evolution'}
            return self.evolution.propose(adapter, goal, history, n)
        return super().propose(adapter, goal, history, n)
