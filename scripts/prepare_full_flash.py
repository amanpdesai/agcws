"""Prepare the declared confirmation-split matrix, never launch it."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write

SEEDS = list(range(9100, 9110))


def config(bank, manifest):
    smoke = runpy.run_path(ROOT / "scripts/prepare_bank_smoke.py")["config"](bank, manifest, 4)
    targets = {name: rates for name, rates in smoke["targets"].items() if name.startswith("confirmation-")}
    if len(targets) != 9:
        raise ValueError("nine confirmation requests required")
    return validate({**smoke, "name": bank["domain"] + "-full-flash-v1", "targets": targets,
                     "seeds": SEEDS.copy(), "budget": 128, "stop_on_success": True,
                     "cost_ceiling_usd": 120.0})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    spec = config(read(args.bank), verify_inputs(ROOT, args.reference))
    args.destination.mkdir(parents=True, exist_ok=False)
    write(args.destination / "config.json", spec)
    prepare(ROOT, args.destination / "config.json", args.destination / "run")
    write(args.destination / "freeze.json", {
        "bank_sha256": hashlib.sha256(args.bank.read_bytes()).hexdigest(),
        "protocol_sha256": hashlib.sha256((ROOT / "docs/FULL_FLASH_V1.md").read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256((args.destination / "config.json").read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256((args.destination / "run/manifest.json").read_bytes()).hexdigest(),
        "ready": False, "launch_authorized": False,
    })
    print({"prepared": True, "executed": False, "cells": 270, "max_slots": 34560})
