"""Fixed-work schedule context and classical operators shared across adapters."""

import copy
import hashlib
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


def history_summary(history):
    """Four best valid plus four recent trials; complete evidence stays in the ledger."""
    selected = history if len(history) <= 8 else sorted(
        {t["slot"]: t for t in [
            *sorted((t for t in history if t["valid"] is True), key=lambda t: (t["loss"], t["slot"]))[:4],
            *history[-4:]]}.values(), key=lambda t: t["slot"])
    rows = []
    for trial in selected:
        row = {k: copy.deepcopy(trial.get(k)) for k in (
            "slot", "program", "valid", "stage", "reason", "rates", "residual", "loss")}
        encoded = json.dumps(row["program"], sort_keys=True).encode()
        if len(encoded) > 12000:
            row["program"] = None
            row["program_omitted"] = {"reason": "history display limit; full submitted program remains in the slot artifact",
                                      "bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()}
        reason = row["reason"]
        if isinstance(reason, str) and len(reason.encode()) > 2000:
            row["reason"] = None
            row["reason_excerpt"] = {"text": reason.encode()[:2000].decode(errors="ignore"),
                                     "sha256": hashlib.sha256(reason.encode()).hexdigest(),
                                     "bytes": len(reason.encode()), "complete": False}
        rows.append(row)
    return rows


def payload(adapter, history, goal, n, *, schema=None):
    summarized = history_summary(history)
    resource_context = {}
    if hasattr(adapter, "contract"):
        resource_context = {"exact_resource_budget": {
            "work_units": adapter.contract.work_units, "idle_cycles": adapter.contract.idle_cycles,
            "max_expanded_operations": adapter.contract.max_expanded_ops,
            "refinement_guidance": "Start from a valid previous schedule when correcting a budget violation. "
                "Reordering its existing operations preserves totals. When editing numeric parameters, "
                "transfer an amount between two operations of the same kind rather than changing totals "
                "independently. Keep each parameter positive and within its bounds. Repeated bodies count "
                "with their full multiplicity. These are suggestions, not automatic repairs."}}
    return json.dumps({
        **resource_context,
        "instruction": "Propose complete schedules to match the eight-bin activity target. "
                       "Return hypothesis and candidates as strict JSON. Never modify the RTL, "
                       "harness or evaluator. Obey the supplied resource constraints; no "
                       "automatic repair is performed. Use prior signed residuals to revise "
                       "timing and ordering, and diversify when the evidence is ambiguous.",
        "design": {"name": adapter.name, "summary": adapter.design_summary,
                   "protocol_constraints": adapter.protocol_constraints},
        "response_schema": schema if schema is not None else response_schema(n, adapter.contract),
        "goal": goal,
        "history_policy": {"version": "best4-recent4-v1", "total_slots": len(history),
                           "shown_slots": [t["slot"] for t in summarized],
                           "omitted_slots": len(history) - len(summarized),
                           "note": "History selection and marked display omissions only; no proposal repair or free retry."},
        "history": summarized,
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
