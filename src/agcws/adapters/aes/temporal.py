"""Fixed AES-128 encryption lowering for the structural temporal pilot."""
from agcws.adapters.aes.transactions import AESTransactionAdapter
from agcws.adapters.base import Validity, ValidityStage
from agcws.workloads.schedule import (
    SCHEDULE_SCHEMA,
    expand_schedule,
    validate_schedule_shape,
)


def lower_schedule(schedule, contract):
    operations = [{'op': 'configure', 'key_len': 128}]
    for node in expand_schedule(schedule, contract):
        operations.append({'op': 'encrypt', 'blocks': node['units']} if node['op'] == 'work'
                          else {'op': 'idle', 'cycles': node['cycles']})
    return {'data_pattern': 1, 'operations': operations}


class AESTemporalAdapter(AESTransactionAdapter):
    workload_schema = SCHEDULE_SCHEMA
    design_summary = ('AES-128 encryption with fixed key/data. A work unit encrypts one block; '
                      'wait cycles pace the core. Sequence order controls temporal activity.')

    def __init__(self, contract):
        self.contract = contract
        self.useful_work_floor = contract.work_units
        self.protocol_constraints = (f'exactly {contract.work_units} work units',
                                     f'exactly {contract.idle_cycles} idle cycles',
                                     'bounded repeat expansion; no implicit repair')

    def validate_schema(self, workload):
        try:
            validate_schedule_shape(workload, self.contract)
        except ValueError as exc:
            return Validity(False, ValidityStage.SCHEMA, str(exc))
        return Validity(True)

    def validate_protocol(self, workload):
        try:
            expand_schedule(workload, self.contract)
        except ValueError as exc:
            return Validity(False, ValidityStage.PROTOCOL, str(exc))
        return Validity(True)

    def elaborate(self, workload):
        return lower_schedule(workload, self.contract)

    def validate_result(self, result):
        validity = super().validate_result(result)
        if validity.valid and result.useful_work != self.contract.work_units:
            return Validity(False, ValidityStage.USEFUL_WORK, 'exact work contract violated')
        return validity
