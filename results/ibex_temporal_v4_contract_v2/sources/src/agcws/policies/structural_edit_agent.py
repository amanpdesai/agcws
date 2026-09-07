"""Typed structural operators with named parents, not arbitrary JSON patches."""
import json
from dataclasses import asdict

from agcws.policies.structural import StructuralPopulationEvolution
from agcws.policies.structural_agent import StructuralAgent
from agcws.policies.structural_population import temporal_population
from agcws.workloads.schedule import expand_schedule
from agcws.workloads.structural_edits import apply_structural_edit

EDIT_CONTRACT = {
    'swap': {'fields': ['op', 'a', 'b'], 'rule': 'swap two different valid indices'},
    'move': {'fields': ['op', 'a', 'b'], 'rule': 'remove a then insert at final index b; a != b'},
    'split': {'fields': ['op', 'a', 'amount'],
              'rule': 'split a into (old - amount, amount); 1 <= amount < count at a; operation cap applies'},
    'merge': {'fields': ['op', 'a', 'b'],
              'rule': 'same op type, a != b; add b into a then delete b'},
    'redistribute': {'fields': ['op', 'a', 'b', 'amount'],
                     'rule': 'same op type, a != b; move amount from a to b; 1 <= amount < count at a'},
}


class StructuralEditAgent(StructuralAgent):
    name = 'structural-edit-agent-v2'

    def select_parents(self, history):
        return sorted((t for t in history if t.validity.valid and t.loss is not None),
                      key=lambda t: t.loss)[:8]

    def build_payload(self, adapter, goal, history, n, system_prompt):
        selected = self.select_parents(history)
        self.parents = {f'parent_{i}': t.workload for i, t in enumerate(selected)}
        parents = []
        for i, trial in enumerate(selected):
            rates = trial.profile.windowed
            parents.append({'parent_id': f'parent_{i}', 'loss': trial.loss,
                            'observed_rates': rates,
                            'signed_residual': [(a-b) / goal.scale for a,b in zip(rates, goal.profile)],
                            'sequence': [{'index': j, **node} for j, node in enumerate(
                                expand_schedule(trial.workload, adapter.contract))]})
        recent = [{'valid': t.validity.valid, 'loss': t.loss,
                   'rejection': t.workload.get('__invalid_structural_edit__', {}).get('reason', t.validity.reason)}
                  for t in history[-8:]]
        return json.dumps({'system_prompt': system_prompt,
                           'design': {'name': adapter.name, 'summary': adapter.design_summary},
                           'contract': asdict(adapter.contract), 'goal': asdict(goal),
                           'parents': parents, 'recent_feedback': recent,
                           'operators': EDIT_CONTRACT, 'batch_size': n,
                           'output_fields': ['parent_id', 'edit'],
                           'indexing': 'a and b are integers indexing the selected parent sequence'}, sort_keys=True)

    def propose(self, adapter, goal, history, n):
        proposals = super().propose(adapter, goal, history, n)
        if not history:
            return proposals
        candidates, failures = [], []
        for slot, proposal in enumerate(proposals):
            try:
                if set(proposal) != {'parent_id', 'edit'}:
                    raise ValueError('expected exactly parent_id and edit')
                parent = self.parents[proposal['parent_id']]
                candidates.append(apply_structural_edit(parent, adapter.contract, proposal['edit']))
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                failure = {'request': proposal, 'reason': str(exc)}
                candidates.append({'__invalid_structural_edit__': failure})
                failures.append({'slot': slot, **failure})
        self.last_diagnostics['structural_edit_failures'] = failures
        return candidates


class StructuralEditHybrid(StructuralEditAgent):
    name = 'structural-edit-hybrid-v2'

    def propose(self, adapter, goal, history, n):
        if history and self.batches % 2 == 0:
            self.batches += 1
            self.last_usage = {'tokens_in': 0, 'tokens_out': 0}
            self.last_diagnostics = {'proposal_source': 'structural_evolution'}
            return self.evolution.propose(adapter, goal, history, n)
        return super().propose(adapter, goal, history, n)


class StructuralPopulationAgent(StructuralEditAgent):
    name = 'structural-population-agent-v1'

    def select_parents(self, history):
        return temporal_population(history)


class StructuralPopulationHybrid(StructuralEditHybrid):
    name = 'structural-population-hybrid-v1'

    def initialize(self, seed):
        super().initialize(seed)
        self.evolution = StructuralPopulationEvolution(seed)
        return self

    def select_parents(self, history):
        return temporal_population(history)
