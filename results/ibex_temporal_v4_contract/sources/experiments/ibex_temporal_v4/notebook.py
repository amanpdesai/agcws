"""Testable public predictions paired with results, never inferred private reasoning."""


def changes(before, after, path=()):
    if type(before) is not type(after):
        return [{"path": list(path), "before": before, "after": after}]
    if isinstance(before, dict) and before.keys() == after.keys():
        return [
            c for k in sorted(before) for c in changes(before[k], after[k], (*path, k))
        ]
    if isinstance(before, list) and len(before) == len(after):
        return [
            c
            for i, (a, b) in enumerate(zip(before, after))
            for c in changes(a, b, (*path, i))
        ]
    return (
        []
        if before == after
        else [{"path": list(path), "before": before, "after": after}]
    )


def assess(trial, history, scale, neutral_band=0.01):
    if scale <= 0 or neutral_band < 0:
        raise ValueError("positive scale and nonnegative neutral band required")
    note = trial.get("prediction")
    result = {
        "slot": trial["slot"],
        "prediction": note,
        "scorable": False,
        "reason": "missing or malformed prediction",
        "actual_changes": None,
    }
    if note is None or trial.get("prediction_error"):
        return result
    references = [t for t in history if t["slot"] == note["reference_slot"]]
    if (
        len(references) != 1
        or not references[0]["valid"]
        or references[0]["slot"] >= trial["slot"]
    ):
        return {**result, "reason": "reference must be one valid prior trial"}
    reference = references[0]
    if trial.get("canonical_program") is not None:
        result["actual_changes"] = changes(
            reference["canonical_program"], trial["canonical_program"]
        )
    if not trial["valid"]:
        return {**result, "reason": "candidate has no valid measurement"}
    if (
        len(trial["rates"]) != 8
        or len(reference["rates"]) != 8
        or len(note["window_directions"]) != 8
    ):
        raise ValueError("eight-bin measurement and prediction required")
    delta = [(a - b) / scale for a, b in zip(trial["rates"], reference["rates"])]
    directions = [0 if abs(d) <= neutral_band else (1 if d > 0 else -1) for d in delta]
    matches = [a == b for a, b in zip(directions, note["window_directions"])]
    return {
        **result,
        "scorable": True,
        "reason": "measured",
        "normalized_delta": delta,
        "neutral_band": neutral_band,
        "observed_directions": directions,
        "matched_bins": sum(matches),
        "total_bins": 8,
        "all_directions_supported": all(matches),
    }


def notebook(history, scale, limit=6, neutral_band=0.01):
    if type(limit) is not int or limit < 1:
        raise ValueError("positive notebook retention required")
    proposed = [t for t in history if t.get("proposal_mode") != "initial"]
    return [assess(t, history, scale, neutral_band) for t in proposed[-limit:]]
