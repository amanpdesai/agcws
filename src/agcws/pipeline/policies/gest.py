"""Strict ask/tell accounting around hash-verified upstream genetic operators."""

import ast
import copy
import hashlib
import math
import random
from pathlib import Path

from agcws.pipeline.ibex.program import canonical, random_program

ROOT = Path(__file__).resolve().parents[4]
HASHES = {
    "Algorithm.py": "4d31f08de6c2a63e57e9dfba5dad82adeba01988a70a8eb1909564f6146abc32",
    "Individual.py": "2142ad5e4a551df378d44a026034a8bbe4494db19b0036a575a21f4f4f9463aa",
    "Population.py": "c16313f16afda685a17bd395e3a9bf9f9e72c81a6bbefea2e3190d70f36807b6",
}
METHODS = {"__tournamentSelection__", "__uniform_crossover__", "__mutation__"}


def upstream(source=None):
    """Compile exact named methods, excluding the hardware runner and imports."""
    source = source or ROOT / "third_party/gest/src"
    data = {}
    for name, expected in HASHES.items():
        raw = (source / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"changed upstream source: {name}")
        data[name] = raw
    namespace = {"__name__": "agcws_gest_operator_capsule"}
    for name in ("Individual.py", "Population.py"):
        exec(compile(data[name], str(source / name), "exec"), namespace)  # noqa: S102 -- hash-verified upstream only
    tree = ast.parse(data["Algorithm.py"])
    original = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Algorithm")
    selected = [n for n in original.body if isinstance(n, ast.FunctionDef) and n.name in METHODS]
    if {n.name for n in selected} != METHODS:
        raise ValueError("upstream operator interface differs")
    capsule = ast.Module(body=selected, type_ignores=[])
    exec(compile(capsule, str(source / "Algorithm.py"), "exec"), namespace)  # noqa: S102 -- exact allowlisted upstream methods
    operators = type("Operators", (), {name: namespace[name] for name in METHODS})
    return namespace["Individual"], namespace["Population"], operators


class Gene:
    """Homogeneous phase locus; locus zero also supplies global program fields."""

    def __init__(self, phase, program):
        self.phase = copy.deepcopy(phase)
        self.registers = list(program["registers"])
        self.memory_seed = program["memory_seed"]
        self.count = len(program["segments"])

    def copy(self):
        return copy.deepcopy(self)

    def getOperands(self):
        return []

    def mutateOperands(self, rng):
        program = random_program(rng)
        self.__init__(rng.choice(program["segments"]), program)


def encode(program):
    program = canonical(program)
    phases = program["segments"]
    return [Gene(phases[i % len(phases)], program) for i in range(8)]


def decode(genes):
    first = genes[0]
    return canonical(
        {
            "registers": list(first.registers),
            "memory_seed": first.memory_seed,
            "segments": [copy.deepcopy(g.phase) for g in genes[: first.count]],
        }
    )


class Bridge:
    def __init__(self, seed, budget):
        if type(seed) is not int or type(budget) is not int or budget < 2 or budget % 2:
            raise ValueError("integer seed and positive even budget >=2 required")
        self.individual, self.population, operators = upstream()
        self.engine = operators()
        self.engine.rand = random.Random(seed)
        self.engine.loopSize = 8
        self.engine.uniformRate = 0.5
        self.engine.mutationRate = 0.2
        self.engine.tournamentSize = 2
        self.engine.allInstructionArray = [
            Gene({}, {"registers": [], "memory_seed": 0, "segments": []})
        ]
        self.budget, self.used = budget, 0
        self._pending, self._valid = [], []

    def ask(self):
        if self._pending:
            raise RuntimeError("tell the whole pending batch before another ask")
        if self.used == self.budget:
            raise RuntimeError("proposal budget exhausted")
        parents = []
        if len(self._valid) < 2:
            children = [
                self.individual(sequence=encode(random_program(self.engine.rand))) for _ in range(2)
            ]
            operator = "bootstrap"
        else:
            self.engine.population = self.population(
                individuals=sorted(self._valid, key=lambda item: (-item.getFitness(), item.slot))[
                    :8
                ]
            )
            chosen = [self.engine.__tournamentSelection__() for _ in range(2)]
            parents = [p.slot for p in chosen]
            self.engine.populationsExamined = self.used // 2
            children = self.engine.__uniform_crossover__(*chosen)
            for child in children:
                self.engine.__mutation__(child)
            operator = "gest-uniform+replacement"
        proposals = []
        for child in children:
            self.used += 1
            child.slot = self.used
            proposal = {
                "slot": self.used,
                "program": decode(child.sequence),
                "operator": operator,
                "parents": parents.copy(),
            }
            self._pending.append((child, copy.deepcopy(proposal)))
            proposals.append(proposal)
        return proposals

    def tell(self, observations):
        if not self._pending or len(observations) != len(self._pending):
            raise ValueError("exact pending batch required")
        for (_, expected), actual in zip(self._pending, observations, strict=True):
            if actual["slot"] != expected["slot"] or actual["program"] != expected["program"]:
                raise ValueError("observation does not match pending proposal")
            if type(actual["valid"]) is not bool:
                raise ValueError("boolean validity required")
            loss = actual["loss"]
            if actual["valid"]:
                if type(loss) not in (int, float) or not math.isfinite(loss) or loss < 0:
                    raise ValueError("valid observation requires nonnegative finite measured loss")
            elif loss is not None or not actual.get("stage") or not actual.get("reason"):
                raise ValueError("invalid observation requires stage/reason and no score")
        for (child, _), actual in zip(self._pending, observations, strict=True):
            if actual["valid"]:
                child.setFitness(-actual["loss"])
                child.parents = []
                self._valid.append(child)
        self._pending = []
