"""Compact semantic edits to valid parents, materialized into the shared DSL."""
import copy
import json

from agcws.policies.semantic import SemanticEvolution


class SemanticEdits(SemanticEvolution):
    name = "semantic-edits-v3"

    def build_payload(self, adapter, goal, history, n, system_prompt):
        payload = json.loads(super().build_payload(adapter, goal, history, n, system_prompt))
        self.parents = [t.workload for t in sorted(
            (t for t in history if t.validity.valid and t.loss is not None),
            key=lambda t: t.loss)[:4]]
        payload['editable_parents'] = self.parents
        payload['output_contract'] = {
            'format': [{'parent': 0, 'edits': [{'path': ['field', 0, 'parameter'], 'value': 1}]}],
            'rules': 'Return one patch object per proposal. Paths address existing scalar fields; '
                     'strings index object keys and integers index arrays. Up to eight edits per proposal. '
                     'Preserve schema and protocol legality. Parent indices start at zero.'}
        return json.dumps(payload, sort_keys=True)

    def propose(self, adapter, goal, history, n):
        if not history:
            return super().propose(adapter, goal, history, n)
        patches = super().propose(adapter, goal, history, n)
        result = []
        for patch in patches:
            try:
                result.append(apply_edits(self.parents, patch))
            except (KeyError, IndexError, TypeError, ValueError):
                result.append({'__invalid_semantic_patch__': patch})
        return result


class SemanticEditsBounded(SemanticEdits):
    name = "semantic-edits-v4"
    thinking_budget = 512
    max_output_tokens = 8192


def apply_edits(parents, patch):
    parent = patch['parent']
    if type(parent) is not int or not 0 <= parent < len(parents):
        raise ValueError('invalid parent index')
    edits = patch['edits']
    if not isinstance(edits, list) or not 1 <= len(edits) <= 8:
        raise ValueError('expected one to eight edits')
    workload = copy.deepcopy(parents[parent])
    for edit in edits:
        path = edit['path']
        if not isinstance(path, list) or not path:
            raise ValueError('expected nonempty path')
        container = workload
        for key in path:
            if isinstance(container, list):
                if type(key) is not int or not 0 <= key < len(container):
                    raise ValueError('invalid array index')
            elif not isinstance(container, dict) or not isinstance(key, str) or key not in container:
                raise ValueError('invalid object key')
            previous, last = container, key
            container = container[key]
        if isinstance(container, (dict, list)) or isinstance(edit['value'], (dict, list)):
            raise ValueError('edits must replace scalar fields')
        previous[last] = edit['value']
    return workload
