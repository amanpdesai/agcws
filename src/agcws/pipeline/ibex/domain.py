"""Four-stage evaluation and measured temporal loss."""

from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.ibex.notebook import assess
from agcws.pipeline.ibex.program import canonical
from agcws.pipeline.metrics import error


def evaluate(proposal, slot, history, manifest, root, mode):
    result, hit = measured(
        proposal["submitted"],
        root,
        manifest["measurement_fingerprint"],
        manifest["runtime"]["image_id"],
    )
    rates = result["profile"]["window_rates"] if result["valid"] else None
    note, note_error = proposal["prediction"], proposal["prediction_error"]
    if note and note["reference_slot"] not in {t["slot"] for t in history if t["valid"]}:
        note_error = "reference was not visible as valid before this batch"
    trial = {
        "slot": slot,
        "program": proposal["submitted"],
        "canonical_program": canonical(proposal["submitted"]) if result.get("cache_id") else None,
        **{
            k: result.get(k)
            for k in (
                "valid",
                "stage",
                "reason",
                "schema_path",
                "allocation",
                "cache_id",
                "feedback",
                "execution",
            )
        },
        "rates": rates,
        "loss": error(rates, manifest["target_rates"], manifest["scale"])
        if rates is not None
        else None,
        "residual": [(a - b) / manifest["scale"] for a, b in zip(rates, manifest["target_rates"])]
        if rates
        else None,
        "prediction": note,
        "prediction_error": note_error,
        "proposal_mode": mode,
        "cache_hit": hit,
        "evaluation_s": result.get("evaluation_s"),
    }
    trial["prediction_assessment"] = assess(trial, history, manifest["scale"])
    return trial
