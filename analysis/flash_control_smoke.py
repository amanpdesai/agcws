"""Audit bounded control smokes, including the second measured-feedback payload."""

import argparse
from collections import Counter
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import source_inventory
from agcws.pipeline.model import MODELS, cost
from agcws.pipeline.storage import read, write


def analyze(root):
    manifest = read(root / "manifest.json")
    spec = manifest["spec"]
    if (spec["budget"] != 6 or spec["batch_size"] != 2 or spec["seeds"] != [8200]
            or list(spec["targets"]) != ["flat_control"]
            or spec["policies"] != ["flash-4096", "phase-random", "phase-ga"]
            or spec["stop_on_success"] is not False):
        raise ValueError("not the frozen control smoke protocol")
    if source_inventory(ROOT, spec["domain"]) != manifest["sources"]:
        raise ValueError("audit source differs from executed source")
    if read(root / "complete.json")["slots"] != 18:
        raise ValueError("incomplete smoke")
    histories, validity = {}, {}
    for arm in spec["policies"]:
        directory = root / "panel/flat_control/8200" / arm
        history = [t for p in sorted(directory.glob("batches/*/trials.json")) for t in read(p)]
        if [t["slot"] for t in history] != list(range(1, 7)):
            raise ValueError("proposal accounting differs")
        histories[arm] = history
        validity[arm] = dict(Counter("VALID" if t["valid"] else t["stage"] for t in history))
        for trial in history:
            if trial["valid"]:
                cached = read(root / "cache" / trial["cache_id"] / "result.json")
                if not cached["valid"] or cached["rates"] != trial["rates"]:
                    raise ValueError("trial differs from measured cache")
            elif trial["loss"] is not None:
                raise ValueError("invalid trial was scored")
    initial = [t["program"] for t in histories["flash-4096"][:2]]
    if any([t["program"] for t in h[:2]] != initial for h in histories.values()):
        raise ValueError("initialization differs between arms")
    design = backend(spec["domain"])
    history = histories["flash-4096"]
    calls = []
    for offset in (2, 4):
        directory = root / "panel/flat_control/8200/flash-4096/batches" / f"{offset+1:03}"
        response = read(directory / "response.json")
        expected = design.payload(history[:offset], {"profile": spec["targets"]["flat_control"],
                                  "scale": spec["scale"], "tolerance": spec["tolerance"]}, 2)
        if read(directory / "input.json")["payload"] != expected:
            raise ValueError("model did not receive the declared measured history")
        if read(directory / "decoded.json") != design.decode(response["raw_text"], 2):
            raise ValueError("saved parsing differs from raw response")
        known = not response["usage_unknown"]
        if known and response["estimated_usd"] != cost("flash-4096", response["tokens_in"], response["tokens_out"]):
            raise ValueError("cost accounting differs")
        calls.append({key: response.get(key) for key in ("tokens_in", "tokens_out", "thinking_tokens",
                     "estimated_usd", "usage_unknown", "model_version", "finish_reasons", "api_error")})
    ready = (all(not c["usage_unknown"] and not c["api_error"] and c["model_version"] == MODELS["flash-4096"] for c in calls)
             and any(t["valid"] for t in history[2:]))
    return {"scope": "control plumbing only; not non-flat qualification or paper inference",
            "domain": spec["domain"], "ready": ready, "shared_initialization": True,
            "second_call_receives_measured_agent_feedback": True, "proposal_slots": 18,
            "generated_agent_valid": sum(t["valid"] for t in history[2:]),
            "validity": validity, "calls": calls,
            "known_cost_usd": sum(c["estimated_usd"] or 0 for c in calls)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, analyze(args.directory))
