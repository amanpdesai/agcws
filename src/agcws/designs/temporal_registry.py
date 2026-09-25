"""Select the workload backend for each supported temporal design."""

from pathlib import Path


class IbexTemporal:
    binary_path = Path("toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system")

    @staticmethod
    def measured(program, root, manifest):
        from agcws.designs.ibex.programs.cache import measured
        return measured(program, root, manifest["measurement_fingerprint"], manifest["runtime"]["image_id"])

    @staticmethod
    def schema(n):
        from agcws.designs.ibex.programs.native_schema import serving_schema
        return serving_schema(n, True)

    @staticmethod
    def random(rng):
        from agcws.designs.ibex.programs.program import random_program
        return random_program(rng)

    @staticmethod
    def propose_classical(arm, rng, slot, history):
        from agcws.baselines.phase import phase_ga, phase_random
        if arm == "phase-random":
            return phase_random(rng, slot), []
        if arm == "phase-ga":
            program, note = phase_ga(rng, slot, history)
            return program, note["parents"]
        raise ValueError(f"unsupported Ibex policy: {arm}")

    @staticmethod
    def payload(history, goal, n):
        from agcws.designs.ibex.programs.prompt import payload
        return payload(history, goal, n, True)

    @staticmethod
    def decode(text, n):
        from agcws.designs.ibex.programs.contract import decode
        return decode(text, n, True)

    @staticmethod
    def evaluate(*args):
        from agcws.designs.ibex.programs.domain import evaluate
        return evaluate(*args)


def backend(domain):
    if domain == "ibex-temporal":
        return IbexTemporal()
    if domain == "aes-temporal":
        from agcws.designs.aes.backend import AesTemporal
        return AesTemporal()
    if domain == "dma-temporal":
        from agcws.designs.dma.backend import DmaTemporal
        return DmaTemporal()
    if domain == "mesh-temporal":
        from agcws.designs.mesh.backend import MeshTemporal
        return MeshTemporal()
    if domain == "redmule-temporal":
        from agcws.designs.redmule.backend import RedmuleTemporal
        return RedmuleTemporal()
    if domain == "redmule-temporal-long":
        from agcws.designs.redmule.backend import RedmuleTemporalLong
        return RedmuleTemporalLong()
    raise ValueError(f"backend not implemented: {domain}")
