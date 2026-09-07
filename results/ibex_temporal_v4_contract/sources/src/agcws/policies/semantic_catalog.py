"""Versioned semantic scalar edits through an explicit, schema-derived catalog."""
import json

from agcws.policies.scalar_edits import editable_fields
from agcws.policies.semantic import SemanticEvolution
from agcws.policies.semantic_edits import apply_edits


def materialize_catalog_patch(parents, catalog, patch):
    edits = patch['edits']
    if not isinstance(edits, list) or not 1 <= len(edits) <= 8:
        raise ValueError('expected one to eight edits')
    resolved = []
    parent = None
    for edit in edits:
        entry = catalog[edit['field']]
        if parent is not None and parent != entry['parent']:
            raise ValueError('all edits must address one parent')
        parent = entry['parent']
        resolved.append({'path': entry['path'], 'value': edit['value']})
    return apply_edits(parents, {'parent': parent, 'edits': resolved})


class SemanticCatalog(SemanticEvolution):
    name = 'semantic-catalog-v5'
    thinking_budget = 512
    max_output_tokens = 8192

    def build_payload(self, adapter, goal, history, n, system_prompt):
        payload = json.loads(super().build_payload(adapter, goal, history, n, system_prompt))
        self.parents = [t.workload for t in sorted(
            (t for t in history if t.validity.valid and t.loss is not None), key=lambda t: t.loss)[:4]]
        self.catalog = {}
        for parent, workload in enumerate(self.parents):
            for index, (path, value, schema) in enumerate(editable_fields(workload, adapter.workload_schema)):
                self.catalog[f'p{parent}f{index}'] = {
                    'parent': parent, 'path': list(path), 'current': value,
                    'bounds': {k: schema[k] for k in ['enum', 'minimum', 'maximum'] if k in schema}}
        payload['editable_fields'] = self.catalog
        payload['output_contract'] = {
            'format': [{'edits': [{'field': 'p0f0', 'value': 1}]}],
            'rules': 'Use only listed field IDs, one to eight edits per proposal, all from one parent. '
                     'Return one proposal per requested slot. Aggregate constraints still apply.'}
        return json.dumps(payload, sort_keys=True)

    def propose(self, adapter, goal, history, n):
        patches = super().propose(adapter, goal, history, n)
        if not history:
            return patches
        candidates = []
        for patch in patches:
            try:
                candidates.append(materialize_catalog_patch(self.parents, self.catalog, patch))
            except (KeyError, IndexError, TypeError, ValueError):
                candidates.append({'__invalid_catalog_patch__': patch})
        return candidates
