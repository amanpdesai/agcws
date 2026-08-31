from agcws.adapters.base import DesignAdapter, SimResult, Validity, ValidityStage

class AESAdapter(DesignAdapter):
    name = "opentitan_aes"
    useful_work_floor = 16
    regions = ["aes_core", "aes_control", "aes_data"]
    workload_schema = {"type": "object", "required": ["operations"], "properties": {"operations": {"type": "array", "maxItems": 256}}, "additionalProperties": False}

    def validate_schema(self, workload: dict) -> Validity:
        ops = workload.get("operations") if isinstance(workload, dict) else None
        if not isinstance(ops, list) or len(ops) > 256:
            return Validity(False, ValidityStage.SCHEMA, "operations must contain at most 256 items")
        return Validity(True)

    def validate_protocol(self, workload: dict) -> Validity:
        configured = False
        for op in workload["operations"]:
            if not isinstance(op, dict) or op.get("op") not in {"configure", "encrypt", "decrypt", "idle"}:
                return Validity(False, ValidityStage.PROTOCOL, "unknown AES operation")
            if op["op"] == "configure": configured = True
            elif op["op"] == "idle":
                if int(op.get("cycles", -1)) < 0 or int(op.get("cycles", -1)) > 10000:
                    return Validity(False, ValidityStage.PROTOCOL, "idle cycles out of range")
            elif not configured: return Validity(False, ValidityStage.PROTOCOL, "configure must precede crypto")
        return Validity(True)

    def elaborate(self, workload: dict) -> list[dict]: return workload["operations"]
    def useful_work(self, result: SimResult) -> float: return result.useful_work
