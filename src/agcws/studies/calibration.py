"""Frozen CPU-only calibration plan for the five-design target bank."""

import statistics
from pathlib import Path

from agcws.core.storage import read, write
from agcws.studies.spec import validate

DOMAINS = ("ibex-temporal", "aes-temporal", "dma-temporal", "mesh-temporal", "redmule-temporal")
SEEDS = (7200, 7201)
BUDGET = 32


def plan(destination, image, ibex_binary):
    """Emit configs only; measurements require the ordinary prepare/run commands."""
    binary = str(Path(ibex_binary).resolve(strict=True))
    destination.mkdir(parents=True, exist_ok=False)
    for domain in DOMAINS:
        spec = {"name": f"five-design-calibration-v1-{domain}", "domain": domain,
                "targets": {"calibration_only": [0.0]*8}, "seeds": list(SEEDS),
                "policies": ["random"], "budget": BUDGET, "batch_size": 2,
                "scale": 1.0, "tolerance": 0.1, "binary": binary if domain == "ibex-temporal" else None,
                "image": image, "max_workers": 2, "cost_ceiling_usd": 1.0, "stop_on_success": False}
        write(destination / f"{domain}.json", validate(spec))
    return {"configs": len(DOMAINS), "slots_per_design": len(SEEDS)*BUDGET, "model_calls": 0}


def report(directory):
    manifest = read(directory / "manifest.json")
    spec = manifest["spec"]
    if (spec["domain"] not in (*DOMAINS, "redmule-temporal-long") or spec["seeds"] != list(SEEDS)
            or spec["policies"] != ["random"] or spec["budget"] != BUDGET
            or spec.get("stop_on_success") is not False
            or spec["targets"] != {"calibration_only": [0.0]*8}):
        raise ValueError("run differs from frozen calibration procedure")
    read(directory / "complete.json")
    trials = [trial for path in sorted((directory / "panel").rglob("trials.json")) for trial in read(path)]
    if len(trials) != len(SEEDS)*BUDGET:
        raise ValueError("incomplete calibration; rejected proposals must remain in the corpus")
    valid = [trial for trial in trials if trial["valid"] is True]
    failures = {}
    for trial in trials:
        if trial["valid"] is not True:
            stage = trial.get("stage", "UNKNOWN")
            failures[stage] = failures.get(stage, 0) + 1
    result = {"domain": spec["domain"], "proposals": len(trials), "valid": len(valid),
              "failure_stages": failures, "measurement_fingerprint": manifest["measurement_fingerprint"],
              "target_qualified": False, "status": "insufficient_valid_calibration"}
    if len(valid) < 32:
        return result
    bins = [rate for trial in valid for rate in trial["rates"]]
    quantiles = statistics.quantiles(bins, n=100, method="inclusive")
    low, high = quantiles[4], quantiles[94]
    mean = statistics.median(statistics.mean(trial["rates"]) for trial in valid)
    result.update(low=low, high=high, scale=high-low, median_window_mean=mean,
                  min_bin=min(bins), max_bin=max(bins),
                  mean_range=[min(statistics.mean(t["rates"]) for t in valid),
                              max(statistics.mean(t["rates"]) for t in valid)],
                  status="calibrated" if high > low and low < mean < high else "degenerate_calibration")
    return result
