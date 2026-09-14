"""Reconstruct every frozen refinement proposal, parent and measured error."""

import argparse
import json
import random
from pathlib import Path

from refine_mesh_witnesses import mutate

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.storage import read
from agcws.pipeline.targets import distance, qualify
from agcws.provenance import file_sha256


def audit(root):
    manifest = read(root / "manifest.json")
    if (manifest["measurement"] != verify_inputs(ROOT, Path(manifest["reference"]))
            or manifest["driver_sha256"] != file_sha256(Path(__file__).with_name("refine_mesh_witnesses.py"))
            or manifest["procedure_sha256"] != file_sha256(ROOT / "docs/MESH_BIT_REFINEMENT_V1.md")):
        raise ValueError("frozen runtime or procedure changed")
    source = Path(manifest["reference"]).parent
    if manifest["source_admission_sha256"] != file_sha256(source / "qualification/admission.json"):
        raise ValueError("original failed admission changed")
    outcomes = []
    for case in manifest["cases"]:
        rng = random.Random(case["seed"])
        parent, error, rates = (case["initial"][k] for k in ("program", "witness_error", "rates"))
        paths = sorted((root / "panel" / case["id"]).glob("*.json"))
        if len(paths) != 512:
            raise ValueError("incomplete refinement")
        for slot, path in enumerate(paths, 1):
            row = read(path)
            program = mutate(parent, rng)
            if row["slot"] != slot or row["program"] != program or row["parent"] != parent:
                raise ValueError("proposal or parent differs")
            measured = row["measurement"]
            if "cache_id" in measured and read(root / "cache" / measured["cache_id"] / "result.json") != measured:
                raise ValueError("measurement cache differs")
            loss = distance(measured["profile"]["window_rates"], case["target"]["rates"], manifest["scale"]) if measured["valid"] else None
            if loss != row["error"]:
                raise ValueError("recorded error differs")
            if loss is not None and loss < error:
                parent, error, rates = program, loss, measured["profile"]["window_rates"]
        outcome = qualify(case["target"], {"valid": True, "rates": rates},
                          scale=manifest["scale"], tolerance=.1, nonflat_margin=.02)
        outcomes.append({"id": case["id"], "program": parent, "rates": rates,
                         "initial_error": case["initial"]["witness_error"], "charged_slots": 512, **outcome})
    expected = {"outcomes": outcomes, "charged_slots": 2048,
                "qualified": sum(r["qualified"] for r in outcomes)}
    if read(root / "complete.json") != expected:
        raise ValueError("refinement summary differs")
    return {"verified": True, "charged_slots": 2048, "qualified": expected["qualified"],
            "scope": "trajectory and cache audit; not independent waveform resimulation"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.root.resolve())))
