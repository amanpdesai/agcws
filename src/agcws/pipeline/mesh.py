"""Mesh traffic phases using the common measured-feedback engine."""

import copy

from agcws.adapters.mesh import MeshTemporalAdapter
from agcws.pipeline import schedules
from agcws.pipeline.schedule_backend import ScheduleTemporal
from agcws.pipeline.storage import read, write


class MeshTemporal(ScheduleTemporal):
    clock_edges = 8200
    scope = "mesh_temporal.dut"

    def adapter(self):
        return MeshTemporalAdapter()

    def canonical(self, program):
        return copy.deepcopy(program)

    def schema(self, n):
        if type(n) is not int or n < 1:
            raise ValueError("positive batch size required")
        return {"type": "object", "additionalProperties": False,
                "required": ["hypothesis", "candidates"], "properties": {
                    "hypothesis": {"type": "string"},
                    "candidates": {"type": "array", "minItems": n, "maxItems": n,
                                   "items": copy.deepcopy(self.adapter().workload_schema)}}}

    def payload(self, history, goal, n):
        return schedules.payload(self.adapter(), history, goal, n, schema=self.schema(n))

    def random(self, rng):
        count = rng.randint(1, 32)
        width = 7936 // count
        phases = []
        for i in range(count):
            phases.append({"start": i * width + rng.randrange(max(1, width // 4)),
                           "duration": rng.randint(1, max(1, width * 3 // 4)),
                           "packets": rng.randint((64 + count - 1) // count, min(512, 4096 // count)),
                           "sources": sorted(rng.sample(range(4), rng.randint(1, 4))),
                           "route": rng.choice(["opposite", "neighbor", "self", "hotspot0"]),
                           "pattern": rng.choice(["zeros", "alternating", "counter"])})
        return {"phases": phases, "sink_period": 8, "sink_pause": rng.randint(0, 3)}

    def propose_classical(self, arm, rng, slot, history):
        if arm == "phase-random":
            return self.random(rng), []
        if arm != "phase-ga":
            raise ValueError(f"unsupported mesh policy: {arm}")
        population = sorted((t for t in history if t["valid"] is True), key=lambda t: t["loss"])[:16]
        if not population or rng.random() < 0.2:
            return self.random(rng), []
        parents = [min(rng.sample(population, min(3, len(population))), key=lambda t: t["loss"])
                   for _ in range(2)]
        child = copy.deepcopy(parents[0]["program"])
        index = rng.randrange(len(child["phases"]))
        child["phases"][index] = copy.deepcopy(rng.choice(parents[1]["program"]["phases"]))
        action = rng.choice(["edit", "insert", "delete"])
        if action == "insert" and len(child["phases"]) < 32:
            child["phases"].insert(index, copy.deepcopy(rng.choice(parents[1]["program"]["phases"])))
        elif action == "delete" and len(child["phases"]) > 1:
            child["phases"].pop(index)
        phase = rng.choice(child["phases"])
        field = rng.choice(["start", "duration", "packets", "route", "pattern", "sources"])
        if field == "start":
            phase[field] = rng.randint(0, 8192 - phase["duration"])
        elif field == "duration":
            phase[field] = rng.randint(1, 8192 - phase["start"])
        elif field == "sources":
            phase[field] = sorted(rng.sample(range(4), rng.randint(1, 4)))
        elif field == "packets":
            phase[field] = rng.randint(1, 512)
        else:
            phase[field] = rng.choice(self.adapter().workload_schema["properties"]["phases"]["items"]["properties"][field]["enum"])
        # Crossover may violate the aggregate count contract. It remains a
        # charged proposal, rejected by the same validator used for the model.
        return child, sorted({p["slot"] for p in parents})

    def invocation(self, program, attempt, relative):
        write(attempt / "workload.json", self.adapter().elaborate(program))
        return ["env", "AGCWS_VERILATOR=/usr/local/bin/verilator", "python3",
                "scripts/run_mesh_workload.py", str(relative / "workload.json"), "--out", str(relative)]

    def failed(self, attempt):
        path = attempt / "run.log"
        if not path.exists():
            return None
        log = path.read_text()
        if "MESH_INCOMPLETE" in log:
            return {"valid": False, "stage": "USEFUL_WORK", "reason": "packets did not drain within the observation window"}
        if "MESH_FUNCTIONAL_MISMATCH" in log:
            return {"valid": False, "stage": "FUNCTIONAL", "reason": "packet scoreboard mismatch"}
        return None

    def completed(self, attempt):
        functional = read(attempt / "functional.json")
        required = len(read(attempt / "workload.json")["packets"])
        if (functional["valid"] is not True or functional["received"] != required
                or functional["sent"] != required or required < self.adapter().useful_work_floor):
            return {"valid": False, "stage": "FUNCTIONAL", "reason": "mesh completion record differs"}
        return {"valid": True, "useful_work": required, "provenance": read(attempt / "provenance.json")}
