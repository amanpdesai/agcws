"""Audit all-target readiness smokes, including actual generated feedback."""

import argparse
from collections import Counter
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.model import MODELS, cost
from agcws.pipeline.provider_schema import provenance
from agcws.pipeline.storage import read, write


def analyze(root):
    manifest = verify_inputs(ROOT, root)
    spec = manifest["spec"]
    protocol = (spec["budget"], spec["seeds"])
    if (protocol not in ((6, [8500]), (16, [8501]), (16, [8502]), (16, [8503])) or spec["batch_size"] != 2
            or len(spec["targets"]) != 18 or spec["stop_on_success"] is not False
            or spec["policies"] != ["flash-4096", "phase-random", "phase-ga"]):
        raise ValueError("not the declared bank smoke")
    complete = read(root / "complete.json")
    if complete["slots"] != 54*spec["budget"] or complete["cells"] != 54:
        raise ValueError("complete 54-cell smoke required")
    design = backend(spec["domain"])
    records = []
    for target, rates in spec["targets"].items():
        histories, validity = {}, {}
        for arm in spec["policies"]:
            cell = root / "panel" / target / str(spec["seeds"][0]) / arm
            history = [t for p in sorted(cell.glob("batches/*/trials.json")) for t in read(p)]
            if [t["slot"] for t in history] != list(range(1, spec["budget"]+1)):
                raise ValueError("proposal accounting differs")
            for trial in history:
                if trial["valid"]:
                    cached = read(root / "cache" / trial["cache_id"] / "result.json")
                    if not cached["valid"] or cached["profile"]["window_rates"] != trial["rates"]:
                        raise ValueError("measured cache differs")
                elif trial["loss"] is not None:
                    raise ValueError("invalid trial scored")
            histories[arm] = history
            validity[arm] = dict(Counter("VALID" if t["valid"] else t["stage"] for t in history))
        initial = [t["program"] for t in histories["flash-4096"][:2]]
        if any([t["program"] for t in h[:2]] != initial for h in histories.values()):
            raise ValueError("shared initialization differs")
        history = histories["flash-4096"]
        calls = []
        for offset in range(2, spec["budget"], 2):
            directory = root / "panel" / target / str(spec["seeds"][0]) / "flash-4096/batches" / f"{offset+1:03}"
            response = read(directory / "response.json")
            expected = design.payload(history[:offset], {"profile": rates, "scale": spec["scale"],
                                      "tolerance": spec["tolerance"]}, 2)
            if read(directory / "input.json")["payload"] != expected:
                raise ValueError("feedback payload differs")
            if read(directory / "decoded.json") != design.decode(response["raw_text"], 2):
                raise ValueError("parsing differs from raw text")
            schema = provenance(design.schema(2))
            if response.get("schema_provenance") != schema:
                raise ValueError("provider schema provenance differs")
            reservation = read(directory / "request_started.json")
            if reservation.get("schema_provenance") != schema:
                raise ValueError("reservation schema provenance differs")
            if not response["usage_unknown"] and response["estimated_usd"] != cost("flash-4096", response["tokens_in"], response["tokens_out"]):
                raise ValueError("cost differs")
            error = response.get("api_error")
            accounted_failure = bool(
                error and error.get("type") == "ServerError"
                and error.get("message", "").startswith("504 DEADLINE_EXCEEDED.")
                and response["usage_unknown"] and response["estimated_usd"] is None
                and response["raw_text"] == "" and reservation["reservation_usd"] > 0
                and all(not t["valid"] and t["stage"] == "API" and t["loss"] is None
                        for t in history[offset:offset+2]))
            ordinary = (not error and not response["usage_unknown"]
                        and response["model_version"] == MODELS["flash-4096"])
            calls.append({**{k: response.get(k) for k in ("tokens_in", "tokens_out", "thinking_tokens",
                           "estimated_usd", "usage_unknown", "model_version", "finish_reasons", "api_error")},
                          "operationally_accounted": ordinary or accounted_failure,
                          "unknown_reserved_usd": reservation["reservation_usd"] if response["usage_unknown"] else 0})
        feedback = any(t["valid"] for t in history[2:spec["budget"]-2])
        successful_calls = all(not c["api_error"] and not c["usage_unknown"] and c["model_version"] == MODELS["flash-4096"] for c in calls)
        records.append({"target": target, "ready": feedback and successful_calls,
                        "operational_ready": feedback and all(c["operationally_accounted"] for c in calls),
                        "measured_generated_feedback": feedback, "validity": validity, "calls": calls})
    markers = set(root.glob("panel/*/*/*/batches/*/request_started.json"))
    responses = {p.parent / "request_started.json" for p in root.glob("panel/*/*/*/batches/*/response.json")}
    if markers != responses or len(markers) != 18*(spec["budget"]-2)//2:
        raise ValueError("unresolved or unexpected provider request")
    return {"scope": "plumbing and measured feedback only, not paper inference", "domain": spec["domain"],
            "ready": all(r["ready"] for r in records), "targets_ready": sum(r["ready"] for r in records),
            "operational_ready": all(r["operational_ready"] for r in records),
            "operational_targets_ready": sum(r["operational_ready"] for r in records),
            "records": records, "charged_slots": 54*spec["budget"],
            "known_cost_usd": sum(c["estimated_usd"] or 0 for r in records for c in r["calls"]),
            "unknown_reserved_usd": sum(c["unknown_reserved_usd"] for r in records for c in r["calls"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, analyze(args.directory))
