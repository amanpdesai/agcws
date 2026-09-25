"""Compact timed traffic phases for the checked 2x2 BaseJump mesh."""

from jsonschema import Draft202012Validator

from agcws.core.contracts import DesignAdapter, Validity, ValidityStage

PHASE = {"type": "object", "additionalProperties": False,
         "required": ["start", "duration", "packets", "sources", "route", "pattern"],
         "properties": {
             "start": {"type": "integer", "minimum": 0, "maximum": 8191},
             "duration": {"type": "integer", "minimum": 1, "maximum": 8192},
             "packets": {"type": "integer", "minimum": 1, "maximum": 512},
             "sources": {"type": "array", "minItems": 1, "maxItems": 4, "uniqueItems": True,
                         "items": {"type": "integer", "minimum": 0, "maximum": 3}},
             "route": {"type": "string", "enum": ["opposite", "neighbor", "self", "hotspot0"]},
             "pattern": {"type": "string", "enum": ["zeros", "alternating", "counter"]},
         }}


class MeshTemporalAdapter(DesignAdapter):
    name = "basejump_mesh_2x2"
    useful_work_floor = 64
    design_summary = (
        "Four buffered routers form a 2x2 XY-routed mesh. Source IDs are x+2*y. "
        "Phases distribute packet releases evenly over a duration and rotate through selected "
        "sources. Opposite routes cross both dimensions; neighbor flips x; self stays local; "
        "hotspot0 concentrates destinations at router 0. Congestion can defer injection and "
        "delivery beyond requested release times. Sink backpressure changes queue occupancy. "
        "Only router hardware activity is measured, not the traffic generator or scoreboard."
    )
    protocol_constraints = (
        "64..4096 packets total; every phase start+duration <=8192",
        "sink_pause < sink_period; source IDs are unique within each phase",
        "all packets must be delivered within 8192 traffic cycles after eight reset cycles",
        "overlapping phases are legal; packet data must remain stable until accepted",
    )
    workload_schema = {"type": "object", "additionalProperties": False,
                       "required": ["phases", "sink_period", "sink_pause"],
                       "properties": {
                           "phases": {"type": "array", "minItems": 1, "maxItems": 32, "items": PHASE},
                           "sink_period": {"type": "integer", "minimum": 1, "maximum": 256},
                           "sink_pause": {"type": "integer", "minimum": 0, "maximum": 255},
                       }}

    def validate_schema(self, workload):
        error = next(Draft202012Validator(self.workload_schema).iter_errors(workload), None)
        return Validity(False, ValidityStage.SCHEMA, error.message) if error else Validity(True)

    def validate_protocol(self, workload):
        if not 64 <= sum(p["packets"] for p in workload["phases"]) <= 4096:
            return Validity(False, ValidityStage.PROTOCOL, "64..4096 scheduled packets required")
        if workload["sink_pause"] >= workload["sink_period"]:
            return Validity(False, ValidityStage.PROTOCOL, "sink must accept some traffic")
        if any(p["start"] + p["duration"] > 8192 for p in workload["phases"]):
            return Validity(False, ValidityStage.PROTOCOL, "phase extends beyond traffic window")
        return Validity(True)

    def elaborate(self, workload):
        for check in (self.validate_schema, self.validate_protocol):
            validity = check(workload)
            if not validity.valid:
                raise ValueError(validity.reason)
        packets = []
        for phase in workload["phases"]:
            for i in range(phase["packets"]):
                source = phase["sources"][i % len(phase["sources"])]
                destinations = {"self": source, "opposite": 3-source, "neighbor": source ^ 1, "hotspot0": 0}
                patterns = {"zeros": 0, "alternating": 0xAAAAAAAA if i % 2 else 0x55555555,
                            "counter": (i * 0x1234567) & 0xFFFFFFFF}
                packets.append({"release_cycle": phase["start"] + i * phase["duration"] // phase["packets"],
                                "source": source, "destination": destinations[phase["route"]],
                                "payload": patterns[phase["pattern"]]})
        packets.sort(key=lambda p: (p["release_cycle"], p["source"]))
        return {"packets": packets, "sink_period": workload["sink_period"], "sink_pause": workload["sink_pause"]}

    def useful_work(self, result):
        return result.useful_work
