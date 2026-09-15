"""Freeze the authorized $10 integration pilot without exposing bank witnesses."""

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256


def main():
    reference = verify_inputs(ROOT, ROOT / "out/bit-activity-v2/ibex/reference")
    bank_path = ROOT / "results/ibex/bit-activity-v2/bank.json"
    bank = read(bank_path)
    if (not bank["task_bank_qualified"]
            or bank["measurement_fingerprint"] != reference["measurement_fingerprint"]):
        raise ValueError("qualified bank and current measurement must match")
    target = next(t for t in bank["splits"]["confirmation"]["requests"] if t["id"] == "alternating")
    if target["constant_floor"] <= .12:
        raise ValueError("pilot requires genuinely nonflat target")
    destination = ROOT / "results/ibex/four-arm-pilot-v1-plan"
    destination.mkdir(parents=True, exist_ok=False)
    spec = {**reference["spec"], "name": "ibex-four-arm-pilot-v1",
            "targets": {"confirmation-alternating": target["rates"]},
            "seeds": [9500, 9501], "policies": ["phase-random", "phase-ga", "flash-4096", "pro-4096"],
            "budget": 128, "batch_size": 2, "stop_on_success": True,
            "scale": bank["calibration"]["scale"], "tolerance": .1,
            "max_workers": 8, "provider_workers": 2, "cost_ceiling_usd": 10.0}
    write(destination / "config.json", spec)
    root = ROOT / "out/ibex-four-arm-pilot-v1"
    manifest = prepare(ROOT, destination / "config.json", root)
    write(destination / "manifest.json", manifest)
    write(destination / "freeze.json", {"bank_sha256": file_sha256(bank_path),
          "config_sha256": file_sha256(destination / "config.json"),
          "manifest_sha256": file_sha256(root / "manifest.json"),
          "scope": "authorized integration pilot, not comparative inference; witnesses excluded",
          "cost_ceiling_usd": 10.0, "cells": 8})
    print(root)


if __name__ == "__main__":
    main()
