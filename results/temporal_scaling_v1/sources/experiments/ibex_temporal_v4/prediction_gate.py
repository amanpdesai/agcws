"""One predeclared request tests the prediction envelope, not search performance."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from agcws import config
from agcws.provenance import file_sha256
from experiments.ibex_temporal_v3.search import error
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.contract_study import digest, verify
from experiments.ibex_temporal_v4.evaluate import write
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.native_schema import serving_schema
from experiments.ibex_temporal_v4.transport import client, request


def freeze(root):
    root.mkdir(parents=True, exist_ok=False)
    old = json.loads(
        Path("results/ibex_temporal_v3_development/manifest.json").read_text()
    )
    gate = Path("results/ibex_temporal_v4_gate/annotated")
    read = lambda name: json.loads((gate / name).read_text())
    program, profile = read("program.json"), read("profile.json")
    target = old["targets"]["target_0"]["rates"]
    scale = old["scale"]
    trial = {
        "slot": 1,
        "program": program,
        "canonical_program": program,
        "valid": True,
        "reason": "",
        "rates": profile["window_rates"],
        "loss": error(profile["window_rates"], target, scale),
        "residual": [(a - b) / scale for a, b in zip(profile["window_rates"], target)],
        "allocation": read("functional.json")["expected"]["allocation"],
        "execution": read("execution.json"),
        "feedback": read("feedback.json"),
        "proposal_mode": "initial",
    }
    contents = payload(
        [trial],
        {"profile": target, "scale": scale, "tolerance": old["tolerance"]},
        2,
        True,
    )
    (root / "inputs").mkdir()
    (root / "inputs/prediction.json").write_text(contents + "\n")
    write(root / "schema.json", serving_schema(2, True))
    previous = json.loads(
        Path("results/ibex_temporal_v4_contract_v2/manifest.json").read_text()
    )
    sources = {Path(p) for p in previous["sources"]} | set(
        Path("experiments/ibex_temporal_v4").glob("*.py")
    )
    sources.add(Path("docs/IBEX_V4_PREDICTION_GATE.md"))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    hashes = {}
    for p in sources:
        if digest(
            subprocess.check_output(["git", "show", f"{commit}:{p}"])
        ) != file_sha256(p):
            raise ValueError(f"uncommitted source: {p}")
        hashes[str(p)] = file_sha256(p)
    write(
        root / "manifest.json",
        {
            "source_commit": commit,
            "sources": hashes,
            "packages": previous["packages"],
            "settings": previous["settings"],
            "schema_sha256": file_sha256(root / "schema.json"),
            "calls": [
                {
                    "name": "prediction",
                    "payload_sha256": file_sha256(root / "inputs/prediction.json"),
                }
            ],
            "gate_inputs": {str(p): file_sha256(p) for p in gate.glob("*.json")},
        },
    )


def run(root):
    manifest = verify(root)
    if digest(
        subprocess.check_output(["git", "show", f"HEAD:{root / 'manifest.json'}"])
    ) != file_sha256(root / "manifest.json"):
        raise ValueError("commit manifest first")
    claim = root / "request_started.json"
    with claim.open("x") as stream:
        json.dump({"manifest_sha256": file_sha256(root / "manifest.json")}, stream)
    config._load_dotenv()
    try:
        result = request(
            client(os.environ["AGCWS_GCP_PROJECT"]),
            manifest["settings"]["model"],
            (root / "inputs/prediction.json").read_text().rstrip("\n"),
            manifest["settings"],
            json.loads((root / "schema.json").read_text()),
        )
    except Exception as exc:
        result = {
            "exception": type(exc).__name__,
            "message": str(exc),
            "raw_text": "",
            "usage_unknown": True,
        }
    result["decoded"] = decode(result["raw_text"], 2, True)
    result["ready"] = (
        not result["usage_unknown"]
        and result["decoded"]["response_error"] is None
        and all(
            s["canonical"] is not None
            and s["prediction"] is not None
            and s["prediction"]["reference_slot"] == 1
            for s in result["decoded"]["slots"]
        )
    )
    write(root / "result.json", result)
    print(
        json.dumps(
            {
                "ready": result["ready"],
                "requested_slots": 2,
                "response_error": result["decoded"]["response_error"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    (freeze if args.action == "freeze" else run)(args.root)
