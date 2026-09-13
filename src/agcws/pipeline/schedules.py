"""Fixed-work schedule context and classical operators shared across adapters."""

import copy
import json

from agcws.workloads.schedule import SCHEDULE_SCHEMA, expand_schedule, random_schedule
from agcws.workloads.structural_edits import random_structural_edit


def response_schema(n, contract):
    if type(n) is not int or n < 1:
        raise ValueError("positive batch size required")

    def node(depth):
        branches = copy.deepcopy(SCHEDULE_SCHEMA["$defs"]["node"]["oneOf"])
        if depth == contract.max_depth:
            branches.pop()
        else:
            branches[-1]["properties"]["body"]["items"] = node(depth + 1)
        for branch in branches:
            branch["properties"]["op"]["enum"] = [branch["properties"]["op"].pop("const")]
        return {"anyOf": branches}

    program = {"type": "object", "additionalProperties": False, "required": ["sequence"],
               "properties": {"sequence": {"type": "array", "minItems": 1, "maxItems": 128,
                                           "items": node(1)}}}
    return {"type": "object", "additionalProperties": False,
            "required": ["hypothesis", "candidates"],
            "properties": {"hypothesis": {"type": "string"}, "candidates": {
                "type": "array", "minItems": n, "maxItems": n, "items": program}}}


def payload(adapter, history, goal, n):
    return json.dumps({
        "instruction": "Propose complete schedules to match the eight-bin activity target. "
                       "Return hypothesis and candidates as strict JSON. Never modify the RTL, "
                       "harness or evaluator. Preserve the exact work and idle totals; no "
                       "automatic repair is performed. Use prior signed residuals to revise "
                       "timing and ordering, and diversify when the evidence is ambiguous.",
        "design": {"name": adapter.name, "summary": adapter.design_summary,
                   "protocol_constraints": adapter.protocol_constraints},
        "response_schema": response_schema(n, adapter.contract),
        "goal": goal,
        "history": [{k: t.get(k) for k in (
            "slot", "program", "valid", "stage", "reason", "rates", "residual", "loss"
        )} for t in history],
    }, sort_keys=True)


def decode(text, n):
    def reject_constant(value):
        raise ValueError(f"nonfinite JSON: {value}")

    response, failure = {}, None
    try:
        response = json.loads(text, parse_constant=reject_constant)
        if not isinstance(response, dict) or not isinstance(response.get("candidates"), list):
            raise ValueError("object with candidates array required")
        if len(response["candidates"]) > n:
            raise ValueError("oversized batch")
    except (ValueError, TypeError) as exc:
        response, failure = {}, str(exc)
    candidates = response.get("candidates", [])
    if len(candidates) != n and failure is None:
        failure = "short batch; missing requested slots are charged"
    return {"response_error": failure, "hypothesis": response.get("hypothesis"), "slots": [
        {"submitted": candidates[i] if i < len(candidates) else None,
         "prediction": None, "prediction_error": None} for i in range(n)
    ]}


def crossover(left, right, contract, rng):
    """Recombine work partitions, idle partitions and ordering from two parents."""
    left = expand_schedule(left, contract)
    right = expand_schedule(right, contract)
    # Each inherited partition already sums to the fixed resource total.
    work = [n["units"] for n in left if n["op"] == "work"]
    waits = [n["cycles"] for n in right if n["op"] == "wait"]
    if len(work) + len(waits) > contract.max_expanded_ops:
        # Bound the internal genotype before it becomes a proposed workload.
        while len(work) + len(waits) > contract.max_expanded_ops:
            values = work if len(work) >= len(waits) else waits
            values[-2:] = [sum(values[-2:])]
    order = [n["op"] for n in rng.choice([left, right])]
    queues = {"work": list(work), "wait": list(waits)}
    sequence = []
    for op in order:
        if queues[op]:
            sequence.append({"op": op, "units" if op == "work" else "cycles": queues[op].pop(0)})
    for op, values in queues.items():
        sequence.extend({"op": op, "units" if op == "work" else "cycles": v} for v in values)
    candidate = {"sequence": sequence}
    expand_schedule(candidate, contract)
    return candidate


def propose_classical(arm, rng, history, contract):
    if arm == "phase-random":
        return random_schedule(rng, contract), []
    if arm != "phase-ga":
        raise ValueError(f"unsupported schedule policy: {arm}")
    population = sorted((t for t in history if t["valid"] is True), key=lambda t: t["loss"])[:16]
    if not population or rng.random() < 0.2:
        return random_schedule(rng, contract), []
    parents = [min(rng.sample(population, min(3, len(population))), key=lambda t: t["loss"])
               for _ in range(2)]
    child = crossover(parents[0]["program"], parents[1]["program"], contract, rng)
    child = random_structural_edit(child, contract, rng)
    return child, sorted({t["slot"] for t in parents})
