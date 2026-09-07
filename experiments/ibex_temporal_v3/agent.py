"""Factorized source-context and corrective-feedback treatments."""

import json

from experiments.ibex_temporal_v2.search import PROMPT, ProgramAgent as BaseAgent
from experiments.ibex_temporal_v3.coverage import BehaviorArchive

CORRECTION = (
    "Use measured instruction mix and completion margin to diagnose the last result. "
    "Refine the reference program in one candidate; explore a different instruction/"
    "dependency or pacing mechanism in the other. Return complete programs, not patches. "
    "A retirement gap alone does not identify a hardware stall cause. State a brief "
    "testable prediction of which window should change and why."
)
SOURCE = (
    "Use the supplied configuration and RTL excerpts. Cite a relevant file and line "
    "in your short hypothesis. Do not assume source features are enabled; check the "
    "configuration. A plausible mechanism must still be checked against measurements."
)


def prompt(context=False, correction=False):
    return (
        PROMPT
        + ("\n" + SOURCE if context else "")
        + ("\n" + CORRECTION if correction else "")
    )


class TemporalAgent(BaseAgent):
    source_context = None
    correction = False

    def build_payload(self, adapter, goal, history, n, system_prompt):
        payload = json.loads(
            super().build_payload(adapter, goal, history, n, system_prompt)
        )
        if self.source_context is not None:
            payload["source_context"] = self.source_context
        if self.correction:
            archive = BehaviorArchive()
            for row in history:
                archive.observe(row)
            best = sorted((t for t in history if t["valid"]), key=lambda t: t["loss"])[
                :2
            ]
            selected = {
                t["slot"]: t
                for t in [*best, *archive.representatives(2), *history[-4:]]
            }
            payload["history"] = [
                {
                    k: t.get(k)
                    for k in (
                        "slot",
                        "program",
                        "valid",
                        "reason",
                        "schema_path",
                        "loss",
                        "rates",
                        "residual",
                        "allocation",
                        "feedback",
                        "reference_slot",
                        "rate_delta_from_reference",
                    )
                }
                for t in selected.values()
            ]
            payload["reference_slot"] = best[0]["slot"] if best else None
            payload["behavior_cells_seen"] = len(archive.elites)
        return json.dumps(payload, sort_keys=True)
