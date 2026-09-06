"""Bounded sequence/repeat DSL for fixed-work temporal experiments."""
from dataclasses import dataclass
from itertools import pairwise

from jsonschema import Draft202012Validator

SCHEDULE_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'type': 'object', 'additionalProperties': False, 'required': ['sequence'],
    'properties': {'sequence': {'type': 'array', 'minItems': 1, 'maxItems': 128,
                                'items': {'$ref': '#/$defs/node'}}},
    '$defs': {'node': {'oneOf': [
        {'type': 'object', 'additionalProperties': False, 'required': ['op', 'units'],
         'properties': {'op': {'const': 'work'},
                        'units': {'type': 'integer', 'minimum': 1, 'maximum': 256}}},
        {'type': 'object', 'additionalProperties': False, 'required': ['op', 'cycles'],
         'properties': {'op': {'const': 'wait'},
                        'cycles': {'type': 'integer', 'minimum': 1, 'maximum': 10000}}},
        {'type': 'object', 'additionalProperties': False, 'required': ['op', 'count', 'body'],
         'properties': {'op': {'const': 'repeat'},
                        'count': {'type': 'integer', 'minimum': 1, 'maximum': 64},
                        'body': {'type': 'array', 'minItems': 1, 'maxItems': 128,
                                 'items': {'$ref': '#/$defs/node'}}}},
    ]}},
}


@dataclass(frozen=True)
class ScheduleContract:
    work_units: int
    idle_cycles: int
    max_expanded_ops: int = 128
    max_depth: int = 4

    def __post_init__(self):
        if (type(self.work_units) is not int or not 1 <= self.work_units <= 256
                or type(self.idle_cycles) is not int or not 0 <= self.idle_cycles <= 10000
                or type(self.max_expanded_ops) is not int or not 1 <= self.max_expanded_ops <= 128
                or type(self.max_depth) is not int or not 1 <= self.max_depth <= 4):
            raise ValueError('invalid schedule contract')


def validate_schedule_shape(workload, contract):
    """Reject oversized trees before recursive schema validation or expansion."""
    pending, count = [(workload, 0)], 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > 2 * contract.max_depth + 3 or count > 2048:
            raise ValueError('schedule tree exceeds depth or node limit')
        if isinstance(item, dict):
            pending.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            pending.extend((v, depth + 1) for v in item)
    error = next(Draft202012Validator(SCHEDULE_SCHEMA).iter_errors(workload), None)
    if error:
        raise ValueError(error.message)


def expand_schedule(workload, contract):
    validate_schedule_shape(workload, contract)
    expanded = []

    def visit(nodes, depth):
        if depth > contract.max_depth:
            raise ValueError('repeat nesting exceeds depth limit')
        for node in nodes:
            if node['op'] == 'repeat':
                for _ in range(int(node['count'])):
                    visit(node['body'], depth + 1)
            else:
                if len(expanded) >= contract.max_expanded_ops:
                    raise ValueError('expanded operation limit exceeded')
                field = 'units' if node['op'] == 'work' else 'cycles'
                expanded.append({'op': node['op'], field: int(node[field])})

    visit(workload['sequence'], 0)
    if sum(n.get('units', 0) for n in expanded) != contract.work_units:
        raise ValueError('schedule violates exact useful-work budget')
    if sum(n.get('cycles', 0) for n in expanded) != contract.idle_cycles:
        raise ValueError('schedule violates exact idle-cycle budget')
    return expanded


def random_schedule(rng, contract):
    """Sample partitions and ordering without policy-specific legality repair."""
    if contract.max_expanded_ops < 2 and contract.idle_cycles:
        raise ValueError('contract cannot express both work and idle')
    units = rng.randint(1, min(16, contract.work_units,
                              contract.max_expanded_ops - bool(contract.idle_cycles)))
    waits = rng.randint(1, min(16, contract.idle_cycles, contract.max_expanded_ops - units)) if contract.idle_cycles else 0

    def partition(total, parts):
        cuts = [0, *sorted(rng.sample(range(1, total), parts - 1)), total]
        return [b - a for a, b in pairwise(cuts)]

    sequence = [{'op': 'work', 'units': v} for v in partition(contract.work_units, units)]
    if waits:
        sequence.extend({'op': 'wait', 'cycles': v} for v in partition(contract.idle_cycles, waits))
    rng.shuffle(sequence)
    return {'sequence': sequence}
