"""One frozen 16-slot corrective-feedback smoke, preserving the failed six-slot panel."""

import argparse
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    base = runpy.run_path(ROOT / "scripts/prepare_bank_smoke.py")["config"](
        read(args.bank), verify_inputs(ROOT, args.reference))
    spec = validate({**base, "name": base["name"].replace("smoke-v2", "smoke-v3"),
                     "seeds": [8501], "budget": 16, "cost_ceiling_usd": 12.0})
    args.directory.mkdir(parents=True, exist_ok=False)
    write(args.directory / "config.json", spec)
    prepare(ROOT, args.directory / "config.json", args.directory / "run")
    print({"cells": 54, "slots": 864, "model_calls_maximum": 126, "executed": False})
