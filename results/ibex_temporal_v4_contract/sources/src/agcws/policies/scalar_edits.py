"""Non-LLM control matching semantic edits' parent pool and editable fields."""
import copy
import random

from jsonschema import Draft202012Validator

from agcws.policies.base import SearchPolicy
from agcws.policies.random_search import RandomSearch


def editable_fields(value, schema, path=()):
    alternatives = schema.get('oneOf', schema.get('anyOf'))
    if alternatives:
        schema = next((s for s in alternatives if Draft202012Validator(s).is_valid(value)), {})
    if isinstance(value, dict):
        return [entry for key, child in value.items()
                for entry in editable_fields(child, schema.get('properties', {}).get(key, {}), path + (key,))]
    if isinstance(value, list):
        return [entry for index, child in enumerate(value)
                for entry in editable_fields(child, schema.get('items', {}), path + (index,))]
    if 'const' not in schema and ('enum' in schema or schema.get('type') == 'integer'):
        return [(path, value, schema)]
    return []


class ScalarEditEvolution(SearchPolicy):
    name = 'scalar-edit-evolution'

    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.initializer = RandomSearch(seed)

    def propose(self, adapter, goal, history, n):
        valid = sorted((t for t in history if t.validity.valid and t.loss is not None), key=lambda t: t.loss)
        if not valid:
            return self.initializer.propose(adapter, goal, history, n)
        candidates = []
        for _ in range(n):
            parent = self.rng.choice(valid[:4]).workload
            child = copy.deepcopy(parent)
            fields = editable_fields(parent, adapter.workload_schema)
            if not fields:
                candidates.append(child)
                continue
            for path, value, schema in self.rng.sample(fields, self.rng.randint(1, min(8, len(fields)))):
                if 'enum' in schema:
                    replacement = self.rng.choice(schema['enum'])
                else:
                    lower = schema.get('minimum', 0)
                    upper = schema.get('maximum', max(lower + 1, value * 2))
                    if self.rng.random() < 0.25:
                        replacement = self.rng.randint(lower, upper)
                    else:
                        replacement = round(value * self.rng.choice([0.5, 0.8, 1.2, 2.0])) + self.rng.choice([-1, 1])
                        replacement = min(upper, max(lower, replacement))
                container = child
                for key in path[:-1]:
                    container = container[key]
                container[path[-1]] = replacement
            candidates.append(child)
        return candidates
