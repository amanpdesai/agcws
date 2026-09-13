"""Explicit backend boundary; never advertise an unimplemented design as runnable."""

from pathlib import Path


class IbexTemporal:
    binary_path = Path("toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system")

    @staticmethod
    def schema(n):
        from agcws.pipeline.ibex.native_schema import serving_schema
        return serving_schema(n, True)

    @staticmethod
    def random(rng):
        from agcws.pipeline.ibex.program import random_program
        return random_program(rng)

    @staticmethod
    def propose_classical(arm, rng, slot, history):
        from agcws.pipeline.policies.phase import phase_ga, phase_random
        if arm == "phase-random":
            return phase_random(rng, slot), []
        if arm == "phase-ga":
            program, note = phase_ga(rng, slot, history)
            return program, note["parents"]
        raise ValueError(f"unsupported Ibex policy: {arm}")

    @staticmethod
    def payload(history, goal, n):
        from agcws.pipeline.ibex.prompt import payload
        return payload(history, goal, n, True)

    @staticmethod
    def decode(text, n):
        from agcws.pipeline.ibex.contract import decode
        return decode(text, n, True)

    @staticmethod
    def evaluate(*args):
        from agcws.pipeline.ibex.domain import evaluate
        return evaluate(*args)


def backend(domain):
    if domain == "ibex-temporal":
        return IbexTemporal()
    if domain == "aes-temporal":
        from agcws.pipeline.aes import AesTemporal
        return AesTemporal()
    if domain == "dma-temporal":
        from agcws.pipeline.dma import DmaTemporal
        return DmaTemporal()
    if domain == "mesh-temporal":
        from agcws.pipeline.mesh import MeshTemporal
        return MeshTemporal()
    raise ValueError(f"backend not implemented: {domain}")
