"""Explicit controls for the matched surrogate/no-screening comparison."""

import copy
import random

from agcws.pipeline.ibex.program import random_program
from agcws.pipeline.policies.gest import Bridge, decode, encode
from agcws.pipeline.policies.phase import phase_ga, phase_random
from agcws.pipeline.policies.screening import Policy as ScreenPolicy

ARMS = (
    "random",
    "phase-random",
    "phase-ga",
    "gest-batch2",
    "gest-pool4",
    "ridge-screen",
)


class NoScreen(ScreenPolicy):
    """Same offspring generation as ScreenPolicy, without fitting or filtering."""

    def ask(self):
        if self._pending:
            raise RuntimeError("pending batch requires complete feedback")
        if self.used == self.budget:
            raise RuntimeError("proposal budget exhausted")
        k = self.kernel
        if self.used == 0:
            children = [
                k.individual(sequence=encode(random_program(k.engine.rand))) for _ in range(4)
            ]
            parents = [[], [], [], []]
        else:
            if len(self._parents) < 2:
                raise ValueError("insufficient measured bootstrap parents; no replacement draws")
            k.engine.population = k.population(
                individuals=sorted(self._parents, key=lambda p: (-p.getFitness(), p.slot))[:8]
            )
            k.engine.populationsExamined = self.used // 4
            children, parents = [], []
            for _ in range(2):
                pair = [k.engine.__tournamentSelection__() for _ in range(2)]
                for child in k.engine.__uniform_crossover__(*pair):
                    k.engine.__mutation__(child)
                    children.append(child)
                    parents.append([p.slot for p in pair])
        batch = [
            {
                "slot": self.used + i + 1,
                "program": decode(child.sequence),
                "parents": parents[i],
                "selected": True,
            }
            for i, child in enumerate(children)
        ]
        self.used += 4
        self._pending = list(zip(children, copy.deepcopy(batch), strict=True))
        return {
            "proposals": batch,
            "decision": {
                "selected_indices": [0, 1, 2, 3],
                "training_slots": [],
                "predicted_rates": None,
                "predicted_losses": None,
                "novelty_squared_distance": None,
            },
        }


class Control:
    def __init__(self, arm, seed, budget, target, scale):
        if arm not in ARMS:
            raise ValueError("unknown policy")
        if type(seed) is not int or type(budget) is not int or budget < 8 or budget % 4:
            raise ValueError("integer seed and budget multiple of four >=8 required")
        self.arm, self.budget, self.used = arm, budget, 0
        self.rng = random.Random(seed)
        self.delegate = None
        if arm in ("gest-pool4", "ridge-screen"):
            self.delegate = (NoScreen if arm == "gest-pool4" else ScreenPolicy)(
                seed, budget, target, scale
            )
        elif arm == "gest-batch2":
            self.delegate = Bridge(seed, budget)
        self.history, self.pending = [], None

    def ask(self):
        if self.pending is not None or self.used >= self.budget:
            raise RuntimeError("pending or exhausted control")
        if self.arm in ("gest-pool4", "ridge-screen"):
            request = self.delegate.ask()
        elif self.arm == "gest-batch2":
            request = {
                "proposals": [{**p, "selected": True} for p in self.delegate.ask()],
                "decision": None,
            }
        else:
            proposals = []
            for slot in range(self.used + 1, self.used + 5):
                if self.used == 0 or self.arm == "random":
                    program, meta = (
                        random_program(self.rng),
                        {"parents": [], "operator": "random"},
                    )
                elif self.arm == "phase-random":
                    program, meta = (
                        phase_random(self.rng, slot),
                        {"parents": [], "operator": "phase-random"},
                    )
                else:
                    program, meta = phase_ga(self.rng, slot, self.history)
                proposals.append({"slot": slot, "program": program, "selected": True, **meta})
            request = {"proposals": proposals, "decision": None}
        self.used += len(request["proposals"])
        self.pending = copy.deepcopy(request)
        return request

    def tell(self, records):
        if self.pending is None or len(records) != len(self.pending["proposals"]):
            raise ValueError("complete pending batch required")
        for proposal, record in zip(self.pending["proposals"], records, strict=True):
            if any(record[k] != v for k, v in proposal.items()):
                raise ValueError("proposal identity differs")
        if self.delegate is not None:
            self.delegate.tell(records)
        self.history.extend(copy.deepcopy(records))
        self.pending = None
