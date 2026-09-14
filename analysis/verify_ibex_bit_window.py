"""Compare corrected Ibex windows against the historical independent time-bin counter."""

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

from agcws.pipeline.ibex.activity import CLOCK, CORE
from agcws.pipeline.ibex.program import HORIZON
from agcws.provenance import file_sha256

REFERENCE = "16112b1338de80de9fdff59e0d26bf0b7bf19279"


def verify(root):
    source = subprocess.check_output(
        ["git", "show", f"{REFERENCE}:src/agcws/pipeline/ibex/activity.py"], text=True)
    function = next(n for n in ast.parse(source).body
                    if isinstance(n, ast.FunctionDef) and n.name == "stream_activity")
    namespace = {"CORE": CORE, "CLOCK": CLOCK, "HORIZON": HORIZON}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "historical-counter", "exec"), namespace)
    records = []
    for name in ("calibration-18", "confirmation-burst", "confirmation-flat_control"):
        row = json.loads((root / "replay/panel" / name / "result.json").read_text())
        result = row["measurement"]
        if result["valid"] is not True:
            raise ValueError("predeclared Ibex recount requires a valid trace")
        profile = result["profile"]
        waveform = root / "replay/cache" / result["cache_id"] / "run/sim.fst"
        with subprocess.Popen(["fst2vcd", str(waveform)], stdout=subprocess.PIPE, text=True) as process:
            try:
                reference = namespace["stream_activity"](
                    process.stdout, profile["begin_tick"], profile["end_tick"])
            finally:
                process.stdout.close()
            if process.wait():
                raise ValueError("FST conversion failed")
        for key in ("window_bit_transitions", "window_rates", "clock_edges", "begin_tick", "end_tick"):
            if profile[key] != reference[key]:
                raise ValueError(f"independent marker-window mismatch: {name}/{key}")
        records.append({"case": name, "waveform_sha256": file_sha256(waveform),
                        "exact_match": True, "reference": reference})
    return {"reference_commit": REFERENCE, "reference_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "scope": "known-state Ibex traces only; independent historical time-bin implementation",
            "records": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.root)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
