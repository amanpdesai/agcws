"""Common exact-work schedule validation independent of hardware interface."""
from agcws.adapters.base import DesignAdapter, Validity, ValidityStage
from agcws.workloads.schedule import (
    SCHEDULE_SCHEMA,
    expand_schedule,
    validate_schedule_shape,
)


class TemporalScheduleAdapter(DesignAdapter):
    workload_schema = SCHEDULE_SCHEMA
    work_quantum = 1

    def __init__(self, contract):
        self.contract = contract
        self.useful_work_floor = contract.work_units * self.work_quantum
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

    def useful_work(self, result):
        return result.useful_work

    def validate_result(self, result):
        validity = super().validate_result(result)
        if validity.valid and result.useful_work != self.useful_work_floor:
            return Validity(False, ValidityStage.USEFUL_WORK, 'exact work contract violated')
        return validity
