"""Timed GEMM phases through the shared measured-feedback engine."""

import copy

from agcws import config
from agcws.adapters.redmule import RedmuleTemporalAdapter
from agcws.pipeline import schedules
from agcws.pipeline.schedule_backend import ScheduleTemporal
from agcws.pipeline.storage import read
from agcws.provenance import file_sha256


def dependencies():
    return config.path_setting("AGCWS_REDMULE_DEPS", "out/redmule-dependencies-v2").resolve(strict=True)


def dependency_inventory():
    root = dependencies()
    if not (root / "preparation.json").is_file():
        raise ValueError("RedMulE dependency preparation is incomplete")
    files = [root / name for name in ("preparation.json", "sources.vlt", "rtl/Bender.lock")]
    files.extend(p for p in (root / "rtl").rglob("*") if p.is_file() and ".git" not in p.parts
                 and (p.suffix in (".sv", ".svh", ".v", ".vh", ".h", ".c", ".S", ".ld", ".py")
                      or p.name in ("Makefile", "Bender.yml")))
    return {".dependencies/" + str(p.relative_to(root)): file_sha256(p) for p in sorted(set(files))}


class RedmuleTemporal(ScheduleTemporal):
    clock_edges = 65536
    scope = "redmule_tb_wrap.i_redmule_tb.i_redmule_wrap"

    def adapter(self):
        return RedmuleTemporalAdapter()

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
        size = rng.choice([4, 8, 16])
        count = rng.randint(1, 8)
        # Initial sampling reserves drain time; the language itself permits later releases.
        width = 54000 // count
        minimum = max(1, (1024 + size**3 * count - 1) // (size**3 * count))
        phases = [{"start": 2000 + i*width, "duration": rng.randint(1, width),
                   "jobs": rng.randint(minimum, max(minimum, 12 // count))} for i in range(count)]
        return {"size": size, "pattern": rng.choice(["zeros", "alternating", "random"]),
                "data_seed": rng.randrange(65536), "phases": phases}

    def propose_classical(self, arm, rng, slot, history):
        if arm == "phase-random":
            return self.random(rng), []
        if arm != "phase-ga":
            raise ValueError(f"unsupported RedMulE policy: {arm}")
        population = sorted((t for t in history if t["valid"] is True), key=lambda t: t["loss"])[:16]
        if not population or rng.random() < 0.2:
            return self.random(rng), []
        parents = [min(rng.sample(population, min(3, len(population))), key=lambda t: t["loss"]) for _ in range(2)]
        child = copy.deepcopy(parents[0]["program"])
        child["phases"][rng.randrange(len(child["phases"]))] = copy.deepcopy(rng.choice(parents[1]["program"]["phases"]))
        action = rng.choice(["edit", "insert", "delete", "size", "pattern", "data_seed"])
        if action == "insert" and len(child["phases"]) < 32:
            child["phases"].append(copy.deepcopy(rng.choice(parents[1]["program"]["phases"])))
        elif action == "delete" and len(child["phases"]) > 1:
            child["phases"].pop(rng.randrange(len(child["phases"])))
        elif action in ("size", "pattern", "data_seed"):
            child[action] = self.random(rng)[action]
        else:
            phase = rng.choice(child["phases"])
            field = rng.choice(["start", "duration", "jobs"])
            bounds = {"start": (0, 65536-phase["duration"]),
                      "duration": (1, 65536-phase["start"]), "jobs": (1, 32)}
            phase[field] = rng.randint(*bounds[field])
        return child, sorted({p["slot"] for p in parents})

    def environment(self):
        return {"AGCWS_CONTAINER_DEPS": str(dependencies())}

    def invocation(self, program, attempt, relative):
        return ["env", "AGCWS_VERILATOR=/usr/local/bin/verilator", "python3",
                "scripts/run_redmule_workload.py", str(relative / "program.json"),
                "--source-list", ".dependencies/sources.vlt", "--out", str(relative)]

    def failed(self, attempt):
        log = "\n".join(p.read_text() for p in (attempt / "run.log", attempt / "driver.log") if p.exists())
        if "REDMULE_INCOMPLETE" in log or "REDMULE_USEFUL_WORK" in log:
            return {"valid": False, "stage": "USEFUL_WORK", "reason": "required GEMM work did not complete within the fixed window"}
        if "[TB] - errors=" in log and "[TB] - errors=00000000" not in log:
            return {"valid": False, "stage": "FUNCTIONAL", "reason": "GEMM reference mismatch"}
        return None

    def completed(self, attempt):
        program = read(attempt / "program.json")
        result = read(attempt / "functional.json")
        jobs = len(self.adapter().elaborate(program))
        if (result["valid"] is not True or result["completed_jobs"] != jobs
                or result["useful_work"] != jobs*program["size"]**3
                or result["checked_outputs"] != jobs*program["size"]**2):
            return {"valid": False, "stage": "FUNCTIONAL", "reason": "GEMM completion record differs"}
        return {"valid": True, "useful_work": result["useful_work"], "provenance": read(attempt / "provenance.json")}
