"""Four charged proposals, two measured picks; surrogate scores never breed."""

import copy
import math

from agcws.pipeline.ibex.program import random_program
from agcws.pipeline.policies.gest import Bridge, decode, encode
from agcws.pipeline.policies.surrogate import screen


class Policy:
    def __init__(self, seed, budget, target, scale):
        if type(budget) is not int or budget < 8 or budget % 4:
            raise ValueError("budget must be a multiple of four, at least eight")
        if (
            len(target) != 8
            or not all(math.isfinite(v) and v >= 0 for v in target)
            or not math.isfinite(scale)
            or scale <= 0
        ):
            raise ValueError("finite eight-bin target and positive scale required")
        self.kernel = Bridge(seed, budget)
        self.used, self.budget = 0, budget
        self.target, self.scale = list(target), scale
        self._pending, self._history, self._parents = [], [], []

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
                offspring = k.engine.__uniform_crossover__(*pair)
                for child in offspring:
                    k.engine.__mutation__(child)
                    children.append(child)
                    parents.append([p.slot for p in pair])
        batch = [
            {
                "slot": self.used + i + 1,
                "program": decode(child.sequence),
                "parents": parents[i],
            }
            for i, child in enumerate(children)
        ]
        # Charge generation before prediction: a fit failure cannot grant free draws.
        self.used += 4
        self._pending = list(zip(children, copy.deepcopy(batch), strict=True))
        decision = (
            {
                "selected_indices": [0, 1, 2, 3],
                "training_slots": [],
                "predicted_rates": None,
                "predicted_losses": None,
                "novelty_squared_distance": None,
            }
            if self.used == 4
            else screen([p["program"] for p in batch], self._history, self.target, self.scale)
        )
        for i, proposal in enumerate(batch):
            proposal["selected"] = i in decision["selected_indices"]
        self._pending = list(zip(children, copy.deepcopy(batch), strict=True))
        return {"proposals": batch, "decision": decision}

    def tell(self, records):
        if not self._pending or len(records) != 4:
            raise ValueError("complete four-slot feedback required")
        for (_, proposal), record in zip(self._pending, records, strict=True):
            if any(
                record[key] != proposal[key] for key in ("slot", "program", "parents", "selected")
            ):
                raise ValueError("feedback does not match pending proposals")
            if not proposal["selected"]:
                if record["status"] != "FILTERED" or any(
                    record.get(k) is not None for k in ("loss", "rates", "valid")
                ):
                    raise ValueError(
                        "unmeasured proposals have unknown validity and no measured score"
                    )
            else:
                if record["status"] != "MEASURED" or type(record["valid"]) is not bool:
                    raise ValueError("selected proposal requires actual evaluation")
                if record["valid"]:
                    rates, loss = record["rates"], record["loss"]
                    if len(rates) != 8 or not all(math.isfinite(v) and v >= 0 for v in rates):
                        raise ValueError("finite measured eight-bin profile required")
                    expected = math.sqrt(
                        sum(
                            ((a - b) / self.scale) ** 2
                            for a, b in zip(rates, self.target, strict=True)
                        )
                        / 8
                    )
                    if (
                        type(loss) not in (int, float)
                        or not math.isfinite(loss)
                        or not math.isclose(loss, expected, abs_tol=1e-12, rel_tol=1e-12)
                    ):
                        raise ValueError("loss does not match measured profile")
                elif (
                    record.get("loss") is not None
                    or record.get("rates") is not None
                    or not record.get("stage")
                    or not record.get("reason")
                ):
                    raise ValueError("rejected evaluation requires reason and no score")
        for (child, _), record in zip(self._pending, records, strict=True):
            if record["status"] == "MEASURED" and record["valid"]:
                child.slot = record["slot"]
                child.setFitness(-record["loss"])
                child.parents = []
                self._parents.append(child)
        self._history.extend(copy.deepcopy(records))
        self._pending = []
