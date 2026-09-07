"""Common proposal contract; optional measured execution and experiment notebook."""

import json

from experiments.ibex_temporal_v2.search import PROMPT, ProgramAgent
from experiments.ibex_temporal_v4.contract import response_schema
from experiments.ibex_temporal_v4.notebook import notebook

OUTPUT = (
    "Return one JSON object with hypothesis, candidates, and predictions. "
    "Candidates are bare complete programs containing registers, memory_seed, segments; "
    "never wrap them in program or history metadata. predictions is a separate array, "
    "one entry per candidate in the same order. Each prediction names one valid prior "
    "reference_slot, a brief changed_factor, and eight window_directions (-1,0,1). "
    "Directions refer to activity differences from that reference, not from the goal; "
    "entries correspond to bins 1 through 8 in order. A normalized difference within "
    "[-0.01,0.01] counts as no change. Missing prediction metadata does not repair "
    "or invalidate a program; it is reported separately. Make candidate one a focused "
    "refinement and candidate two an exploration. Both consume proposal budget."
)
GROUNDING = (
    "Use executed operand events to check that the intended mechanism occurred. "
    "Zero numerator is not zero divisor. Register values can change inside loops. "
    "Phase times are retirement times, not issue times. Polling and the final wait "
    "execute instructions and contribute activity. A late release request does not "
    "rewind time or prove actual execution placement. Do not label retirement gaps "
    "as a particular stall without evidence. Consult the notebook: retain or reject "
    "prior predictions based on measured outcomes. Prefer a focused reference edit "
    "for candidate one; do not claim causal isolation when several factors changed."
)


def payload(history, goal, n, grounded=False):
    # Replace the old two-field output instruction; keep its workload semantics.
    instruction = PROMPT.replace(
        'Return strict JSON {"hypothesis": "short testable prediction", "candidates": [programs]}.',
        OUTPUT,
    )
    if grounded:
        instruction += "\n" + GROUNDING
    value = json.loads(ProgramAgent.build_payload(None, goal, history, n, instruction))
    value["response_contract"] = response_schema(n, predictions=True)
    if grounded:
        by_slot = {t["slot"]: t for t in history}
        for row in value["history"]:
            trial = by_slot[row["slot"]]
            row["execution"] = trial.get("execution")
            row["feedback"] = trial.get("feedback")
            row["schema_path"] = trial.get("schema_path")
        value["experiment_notebook"] = notebook(history, goal["scale"])
    return json.dumps(value, sort_keys=True)
