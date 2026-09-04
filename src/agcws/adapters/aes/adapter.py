import random

from agcws.adapters.base import DesignAdapter, SimResult, Validity, ValidityStage

class AESAdapter(DesignAdapter):
    name = "opentitan_aes"
    design_summary = ("OpenTitan AES is a command-driven block cipher. Workload knobs are key length, "
                      "encrypt/decrypt direction, block grouping, data pattern, and idle gaps. "
                      "The control and round/data paths are the primary activity regions.")
    protocol_constraints = ("configure must precede encrypt/decrypt", "key length is 128, 192, or 256",
                            "crypto operations use whole positive block counts", "idle cycles are 0..10000")
    useful_work_floor = 38
    regions = ["aes_core", "aes_control", "aes_data"]
    activity_region_prefixes = {
        "aes_control": ("state_", "ctrl_", "in_ready", "out_valid", "key_", "start_"),
        "aes_data": ("data_", "state_d", "state_q", "round_key", "sbox"),
        "aes_core": ("aes_", "round", "mix_", "shift_", "sub_"),
    }
    workload_schema = {
        "type": "object", "required": ["operations"],
        "properties": {
            "operations": {"type": "array", "maxItems": 256, "items": {
                "oneOf": [
                    {"type": "object", "properties": {"op": {"const": "configure"}, "key_len": {"enum": [128, 192, 256]}}, "required": ["op", "key_len"], "additionalProperties": False},
                    {"type": "object", "properties": {"op": {"enum": ["encrypt", "decrypt"]}, "blocks": {"type": "integer", "minimum": 1, "maximum": 256}}, "required": ["op", "blocks"], "additionalProperties": False},
                    {"type": "object", "properties": {"op": {"const": "idle"}, "cycles": {"type": "integer", "minimum": 0, "maximum": 10000}}, "required": ["op", "cycles"], "additionalProperties": False}
                ]
            }},
            "data_pattern": {"type": "integer", "minimum": 0, "maximum": 3}
        }, "additionalProperties": False
    }

    def random_workload(self, rng: random.Random) -> dict:
        """Sample materially different legal transaction schedules.

        Varying only the key length leaves the AES core nearly saturated. This
        samples transaction count, crypto direction, key size, data pattern,
        block grouping, and inter-block gaps while retaining the work floor.
        """
        total = rng.randint(self.useful_work_floor, 256)
        chunks = rng.randint(1, min(8, total))
        remaining, blocks = total, []
        for index in range(chunks - 1):
            minimum = chunks - index - 1
            value = rng.randint(1, remaining - minimum)
            blocks.append(value)
            remaining -= value
        blocks.append(remaining)
        operations = [{"op": "configure", "key_len": rng.choice((128, 192, 256))}]
        idle_budget = 10_000
        for index, count in enumerate(blocks):
            operations.append({"op": rng.choice(("encrypt", "decrypt")), "blocks": count})
            if index != len(blocks) - 1:
                choices = tuple(value for value in (0, 1, 4, 16, 128, 1024, 5000)
                                if value <= idle_budget)
                gap = rng.choice(choices)
                idle_budget -= gap
                operations.append({"op": "idle", "cycles": gap})
        return {"operations": operations, "data_pattern": rng.randrange(4)}

    def validate_schema(self, workload: dict) -> Validity:
        if not isinstance(workload, dict):
            return Validity(False, ValidityStage.SCHEMA, "workload must be an object")
        if set(workload) - {"operations", "data_pattern"}:
            return Validity(False, ValidityStage.SCHEMA, "unknown workload field")
        ops = workload.get("operations") if isinstance(workload, dict) else None
        if not isinstance(ops, list) or len(ops) > 256:
            return Validity(False, ValidityStage.SCHEMA, "operations must contain at most 256 items")
        if not isinstance(workload.get("data_pattern", 0), int) or workload.get("data_pattern", 0) not in range(4):
            return Validity(False, ValidityStage.SCHEMA, "data_pattern must be an integer in [0,3]")
        allowed = {"configure": {"op", "key_len"}, "encrypt": {"op", "blocks"},
                   "decrypt": {"op", "blocks"}, "idle": {"op", "cycles"}}
        for operation in ops:
            if not isinstance(operation, dict) or operation.get("op") not in allowed:
                continue
            if set(operation) - allowed[operation["op"]]:
                return Validity(False, ValidityStage.SCHEMA, "unknown operation field")
        return Validity(True)

    def validate_protocol(self, workload: dict) -> Validity:
        configured = False
        for op in workload["operations"]:
            if not isinstance(op, dict) or op.get("op") not in {"configure", "encrypt", "decrypt", "idle"}:
                return Validity(False, ValidityStage.PROTOCOL, "unknown AES operation")
            if op["op"] == "configure":
                if op.get("key_len", 128) not in {128, 192, 256}:
                    return Validity(False, ValidityStage.PROTOCOL, "key_len must be 128, 192, or 256")
                configured = True
            elif op["op"] == "idle":
                if int(op.get("cycles", -1)) < 0 or int(op.get("cycles", -1)) > 10000:
                    return Validity(False, ValidityStage.PROTOCOL, "idle cycles out of range")
            elif not configured: return Validity(False, ValidityStage.PROTOCOL, "configure must precede crypto")
        return Validity(True)

    def elaborate(self, workload: dict) -> list[dict]: return workload["operations"]
    def useful_work(self, result: SimResult) -> float: return result.useful_work
