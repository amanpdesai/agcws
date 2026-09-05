"""Strict schema and aggregate limits for the versioned transaction harness."""
from jsonschema import Draft202012Validator

from agcws.adapters.aes.adapter import AESAdapter
from agcws.adapters.base import Validity, ValidityStage


class AESTransactionAdapter(AESAdapter):
    protocol_constraints = (*AESAdapter.protocol_constraints,
                            'total encrypted/decrypted blocks must be 1..256',
                            'total idle cycles across all operations must be <=10000')
    validator = Draft202012Validator(AESAdapter.workload_schema)

    def validate_schema(self, workload):
        error = next(self.validator.iter_errors(workload), None)
        if error:
            return Validity(False, ValidityStage.SCHEMA, error.message)
        return Validity(True)

    def validate_protocol(self, workload):
        result = super().validate_protocol(workload)
        if not result.valid:
            return result
        blocks = sum(op.get('blocks', 0) for op in workload['operations'])
        idle = sum(op.get('cycles', 0) for op in workload['operations'])
        if not 1 <= blocks <= 256 or idle > 10000:
            return Validity(False, ValidityStage.PROTOCOL, 'aggregate block or idle limit exceeded')
        return Validity(True)
