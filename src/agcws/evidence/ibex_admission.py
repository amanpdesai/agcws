"""Read-only selection check for the archived 216-attempt Ibex admission panel."""

from agcws.reporting.metrics import error
from agcws.studies.targets import qualify


def select(config, complete):
    if complete["charged_slots"] != 216 or len(complete["results"]) != 216:
        raise ValueError("complete original witness search required")
    scale = config["bank"]["calibration"]["scale"]
    cases = []
    for split, part in config["bank"]["splits"].items():
        for request in part["requests"]:
            name = f"{split}-{request['id']}"
            candidates = [r for r in complete["results"] if r["request_id"] == name and r["measurement"]["valid"]]
            if not candidates:
                raise ValueError("request has no valid witness")
            best = min(candidates, key=lambda r: (error(r["measurement"]["profile"]["window_rates"], request["rates"], scale), r["id"]))
            witness = {**best["measurement"], "rates": best["measurement"]["profile"]["window_rates"]}
            checked = {"id": name, "witness_case": best["id"],
                       **qualify(request, witness, scale=scale, tolerance=.1, nonflat_margin=.02)}
            if checked not in complete["reports"] or not checked["qualified"]:
                raise ValueError("original qualification differs or fails")
            cases.append({"id": name, "split": split, "request": request,
                          "program": best["program"], "expected": best["measurement"]})
    if len(cases) != 18:
        raise ValueError("eighteen requests required")
    return cases
