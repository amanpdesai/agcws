"""Behavior-grid archive and coverage-guided mutation, not RTL code coverage."""

from experiments.ibex_temporal_v3.program import mutate, random_program

WORK_CLASSES = ("alu", "multiply", "divide", "load", "store")


def descriptor(feedback):
    width = feedback["cycles_per_bin"]
    gaps = feedback["cycles_without_retirement"]
    if width <= 0 or len(gaps) != 8 or any(not 0 <= g <= width for g in gaps):
        raise ValueError("eight valid retirement-gap bins required")
    classes = feedback["retired_classes"]
    if len(classes) != 8:
        raise ValueError("eight instruction-class bins required")
    totals = [sum(c[name] for c in classes) for name in WORK_CLASSES]
    dominant = max(range(len(totals)), key=lambda i: totals[i])
    return (*[min(3, 4 * g // width) for g in gaps], dominant)


class BehaviorArchive:
    def __init__(self):
        self.elites = {}
        self.visits = {}

    def observe(self, trial):
        if not trial["valid"]:
            return False
        cell = descriptor(trial["feedback"])
        previous = self.elites.get(cell)
        new = previous is None
        if new or trial["loss"] < previous["loss"]:
            self.elites[cell] = trial
        return new

    def propose(self, rng):
        if not self.elites or rng.random() < 0.2:
            return random_program(rng), {"mode": "restart", "parent_slot": None}
        minimum = min(self.visits.get(cell, 0) for cell in self.elites)
        choices = sorted(
            cell for cell in self.elites if self.visits.get(cell, 0) == minimum
        )
        cell = rng.choice(choices)
        self.visits[cell] = minimum + 1
        parent = self.elites[cell]
        return mutate(parent["program"], rng), {
            "mode": "archive-guided-mutation",
            "parent_slot": parent["slot"],
            "cell": list(cell),
        }

    def representatives(self, n=4):
        cells = sorted(self.elites, key=lambda c: (self.visits.get(c, 0), c))
        return [self.elites[cell] for cell in cells[:n]]
