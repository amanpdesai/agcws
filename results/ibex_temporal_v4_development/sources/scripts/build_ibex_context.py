"""Prepare only approved RTL/spec files for a future source-context ablation."""

import argparse
import json
from pathlib import Path

from agcws.policies.source_context import build_bundle

FILES = [
    "specs/ibex.md",
    "third_party/ibex/examples/simple_system/ibex_simple_system.core",
    "third_party/ibex/examples/simple_system/rtl/ibex_simple_system.sv",
    *[
        f"third_party/ibex/rtl/{name}.sv"
        for name in (
            "ibex_pkg",
            "ibex_core",
            "ibex_cs_registers",
            "ibex_multdiv_fast",
            "ibex_load_store_unit",
            "ibex_decoder",
            "ibex_id_stage",
            "ibex_controller",
        )
    ],
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_bundle(Path.cwd(), args.out, FILES), indent=2))
