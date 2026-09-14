"""Audit frozen DMA timing corners and apply the predeclared window rule."""

import argparse
import hashlib
import math
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.dma import DmaTemporal
from agcws.pipeline.metrics import key
from agcws.pipeline.storage import read, write


def candidate_window(ends):
    if not ends or any(not math.isfinite(v) or v < 0 for v in ends):
        raise ValueError("nonnegative finite schedule ends required")
    horizon = math.ceil((max(ends)+256)/128)*128
    if horizon >= 12000:
        raise ValueError("diagnostic does not justify shortening the old window")
    return horizon


def analyze(root, development, confirmation, expected_horizon=12000):
    if expected_horizon not in (12000, 9216):
        raise ValueError("only declared old/new window versions may be audited")
    digest = hashlib.sha256()

    def record(path):
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        return read(path)

    manifest = record(root / "manifest.json")
    if record(root / "freeze.json") != {"manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()}:
        raise ValueError("diagnostic manifest changed")
    if manifest["config"] != runpy.run_path(ROOT / "analysis/dma_timing_probe.py")["config"]():
        raise ValueError("diagnostic cases differ from declared corners")
    expected_driver = hashlib.sha256((ROOT / "scripts/probe_fixed_cases.py").read_bytes()).hexdigest()
    if manifest["driver_sha256"] != expected_driver:
        raise ValueError("diagnostic driver differs")
    summary = record(root / "complete.json")
    if summary["charged_slots"] != 12 or len(summary["results"]) != 12:
        raise ValueError("incomplete or repeated corner cases")
    design = DmaTemporal()
    timing = runpy.run_path(ROOT / "analysis/dma_window_audit.py")["timing"]
    rows = []
    for case, row in zip(manifest["config"]["cases"], summary["results"], strict=True):
        if row["id"] != case["id"] or row["program"] != case["program"]:
            raise ValueError("terminal result differs from frozen case")
        if record(root / "panel" / case["id"] / "result.json") != row:
            raise ValueError("case checkpoint differs")
        result = row["measurement"]
        if not result["valid"]:
            raise ValueError("all twelve corners must pass before window selection")
        canonical = design.canonical(case["program"])
        identifier = key({"program": canonical, "measurement": manifest["measurement"]["measurement_fingerprint"]})
        if identifier != result["cache_id"]:
            raise ValueError("cache identity differs")
        cache = root / "cache" / identifier
        if record(cache / "result.json") != result:
            raise ValueError("cached measurement differs")
        matches = list(cache.glob("attempt-*/activity.json"))
        if len(matches) != 1:
            raise ValueError("ambiguous activity evidence")
        attempt = matches[0].parent
        if record(attempt / "program.json") != canonical:
            raise ValueError("executed program differs")
        observed = record(attempt / "sim_build/observed.json")
        activity = record(matches[0])
        samples = activity["per_cycle_toggles"]
        if activity["clock_edges"] != expected_horizon or len(samples) != expected_horizon:
            raise ValueError("corner measurement used a different window")
        width = expected_horizon//8
        rates = [sum(samples[i*width:(i+1)*width])/width for i in range(8)]
        if (result["rates"] != rates or result["profile"]["scope"] != "axi_dma"
                or result["profile"]["clock_edges"] != expected_horizon
                or result["profile"]["fidelity"] != "activity"):
            raise ValueError("DUT profile does not reconstruct")
        rows.append({"id": case["id"], **timing(observed, expected_horizon), "rates": rates})
    prior = [record(path) for path in (development, confirmation)]
    if any(p["slots"] != 4608 or p["unique_valid"] <= 0 for p in prior):
        raise ValueError("completed v2 corpus timing audits required")
    ends = [r["schedule_end_cycles"] for r in rows]
    ends.extend(p["timing"]["schedule_end_cycles"]["max"] for p in prior)
    result = {"scope": "timing-based candidate window; not new-window qualification or policy evidence",
            "old_horizon_cycles": 12000, "candidate_horizon_cycles": candidate_window(ends),
            "maximum_observed_schedule_end_cycles": max(ends), "guard_cycles": 256,
            "round_up_multiple": 128, "all_corners_valid": True, "cases": rows,
            "input_evidence_sha256": digest.hexdigest(), "new_measurement_ready": False}
    if expected_horizon != 12000:
        if result["candidate_horizon_cycles"] != expected_horizon:
            raise ValueError("replayed corner timing contradicts the selected horizon")
        result.update(observation_horizon_cycles=expected_horizon, new_window_corners_verified=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--confirmation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-horizon", type=int, choices=(12000, 9216), default=12000)
    args = parser.parse_args()
    write(args.output, analyze(args.directory, args.development, args.confirmation, args.expected_horizon))
