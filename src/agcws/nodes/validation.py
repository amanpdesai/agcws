from agcws.adapters.base import DesignAdapter, Validity, ValidityStage

def validate_workload(adapter: DesignAdapter, workload: dict) -> Validity:
    """Run the shared hard-gate validation stages in order."""
    result = adapter.validate_schema(workload)
    if not result.valid:
        return result
    result = adapter.validate_protocol(workload)
    if not result.valid:
        return result
    return Validity(True)
