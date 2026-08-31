from agcws.adapters.base import DesignAdapter, Validity

def validate_static(adapter: DesignAdapter, workload: dict) -> Validity:
    """Run only pure SCHEMA and PROTOCOL validation."""
    result = adapter.validate_schema(workload)
    if not result.valid:
        return result
    result = adapter.validate_protocol(workload)
    if not result.valid:
        return result
    return Validity(True)

def validate_workload(adapter: DesignAdapter, workload: dict, result) -> Validity:
    """Run the complete four-stage gate when a simulation result is available."""
    static = validate_static(adapter, workload)
    if not static.valid:
        return static
    return adapter.validate_result(result)
