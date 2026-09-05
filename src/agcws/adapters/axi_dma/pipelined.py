"""Executable descriptor concurrency with bounded memory and backpressure."""
import copy

from jsonschema import Draft202012Validator

from agcws.adapters.axi_dma.adapter import AxiDmaAdapter
from agcws.adapters.base import Validity, ValidityStage


def groups(transfers):
    group = []
    for transfer in transfers:
        limit = min([t.get('outstanding', 1) for t in group] + [transfer.get('outstanding', 1)])
        if group and len(group) >= limit:
            yield group
            group = []
        group.append(transfer)
    if group:
        yield group


class PipelinedDmaAdapter(AxiDmaAdapter):
    workload_schema = copy.deepcopy(AxiDmaAdapter.workload_schema)
    workload_schema['properties']['backpressure'] = {
        'type': 'object', 'additionalProperties': False,
        'required': ['period', 'read_pause', 'write_pause'],
        'properties': {'period': {'type': 'integer', 'minimum': 1, 'maximum': 64},
                       'read_pause': {'type': 'integer', 'minimum': 0, 'maximum': 63},
                       'write_pause': {'type': 'integer', 'minimum': 0, 'maximum': 63}}}
    validator = Draft202012Validator(workload_schema)
    protocol_constraints = (*AxiDmaAdapter.protocol_constraints,
                            'mapped memory is [0,65536); both source and destination must fit',
                            'read_pause and write_pause must be less than backpressure period',
                            'overlapping memory ranges across a concurrent group are disallowed',
                            'outstanding limits group size; each group completes before the next')

    def validate_schema(self, workload):
        error = next(self.validator.iter_errors(workload), None)
        return Validity(False, ValidityStage.SCHEMA, error.message) if error else Validity(True)

    def validate_protocol(self, workload):
        result = super().validate_protocol(workload)
        if not result.valid:
            return result
        pause = workload.get('backpressure', {'period': 1, 'read_pause': 0, 'write_pause': 0})
        if max(pause['read_pause'], pause['write_pause']) >= pause['period']:
            return Validity(False, ValidityStage.PROTOCOL, 'backpressure must allow progress')
        for group in groups(workload['transfers']):
            ranges = []
            for transfer in group:
                for field in ('src', 'dst'):
                    start, end = transfer[field], transfer[field] + transfer['length']
                    if start < 0 or end > 65536 or (start & 4095) + transfer['length'] > 4096:
                        return Validity(False, ValidityStage.PROTOCOL, 'memory range or page boundary violation')
                    if any(start < b and a < end for a, b in ranges):
                        return Validity(False, ValidityStage.PROTOCOL, 'overlapping concurrent memory ranges')
                    ranges.append((start, end))
        return Validity(True)

    def random_workload(self, rng):
        workload = super().random_workload(rng)
        depth = rng.choice([1, 2, 4, 8])
        for index, transfer in enumerate(workload['transfers']):
            transfer['src'] = index * 4096 + transfer['src'] % 4096
            transfer['dst'] = (index + 8) * 4096 + transfer['dst'] % 4096
            transfer['outstanding'] = depth
        period = rng.choice([4, 8, 16])
        workload['backpressure'] = {'period': period, 'read_pause': rng.randrange(period),
                                    'write_pause': rng.randrange(period)}
        return workload

    def mutate_workload(self, workload, rng):
        candidate = copy.deepcopy(workload)
        transfer = rng.choice(candidate['transfers'])
        choice = rng.randrange(4)
        if choice == 0:
            transfer['gap_cycles'] = rng.randrange(401)
        elif choice == 1:
            room = min(4096 - transfer['src'] % 4096, 4096 - transfer['dst'] % 4096)
            transfer['length'] = rng.randrange(1, room // 8 + 1) * 8
        elif choice == 2:
            for item in candidate['transfers']:
                item['outstanding'] = rng.choice([1, 2, 4, 8])
        else:
            pause = candidate.setdefault('backpressure', {'period': 8, 'read_pause': 0, 'write_pause': 0})
            pause[rng.choice(['read_pause', 'write_pause'])] = rng.randrange(pause['period'])
        return candidate
