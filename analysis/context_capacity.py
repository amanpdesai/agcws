"""Offline capacity test using repeated measured workloads, not simulated policy results."""

import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path

from agcws.pipeline.backends import backend
from agcws.pipeline.storage import read, write


def capacity(design, trial, goal):
    schema_bytes = len(json.dumps(design.schema(2)).encode())
    rows = []
    for length in (2, 14, 30, 62, 126):
        history = [{**copy.deepcopy(trial), "slot": slot} for slot in range(1, length+1)]
        payload_bytes = len(design.payload(history, goal, 2).encode())
        total = payload_bytes + schema_bytes + 4096
        rows.append({"history_slots": length, "payload_bytes": payload_bytes,
                     "guard_bytes": total, "fits_current_200000_byte_guard": total <= 200000})
    return rows


def analyze(root):
    manifest = read(root / "manifest.json")
    spec = manifest["spec"]
    design = backend(spec["domain"])
    candidates = []
    for path in sorted((root / "panel").glob("*/*/*/batches/*/trials.json")):
        target = path.relative_to(root / "panel").parts[0]
        for trial in read(path):
            if trial["valid"] is True:
                candidates.append((len(json.dumps(trial["program"]).encode()), str(path), target, trial))
    if not candidates:
        raise ValueError("a measured valid workload is required")
    _, source, target, trial = max(candidates, key=lambda row: (row[0], row[1], row[3]["slot"]))
    goal = {"profile": spec["targets"][target], "scale": spec["scale"], "tolerance": spec["tolerance"]}
    return {"domain": spec["domain"], "scope": "synthetic repeated-valid-workload capacity check; not an observed trajectory",
            "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "payload_source_sha256": hashlib.sha256(Path(inspect.getsourcefile(design.payload)).read_bytes()).hexdigest(),
            "source": source, "source_sha256": hashlib.sha256(Path(source).read_bytes()).hexdigest(),
            "source_slot": trial["slot"], "target": target,
            "program_sha256": hashlib.sha256(json.dumps(trial["program"], sort_keys=True).encode()).hexdigest(),
            "rows": capacity(design, trial, goal)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, {"designs": [analyze(path) for path in args.directory], "model_calls": 0})
