"""Freeze and run the supervised development panel; no detached workers."""

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

from agcws import config
from agcws.provenance import file_sha256
from experiments.ibex_temporal_v1.search import PROMPT, error, key


def freeze(root, destination):
    config._load_dotenv()
    gate = json.loads((root / "gate.json").read_text())
    targets = {
        k: {
            "rates": v["window_rates"],
            "witness_sha256": file_sha256(root / "gate-inputs" / f"{k}.json"),
        }
        for k, v in gate.items()
        if k.startswith("target_")
    }
    rates = [x for t in targets.values() for x in t["rates"]]
    scale = max(rates) - min(rates)
    separation = min(
        error(a["rates"], b["rates"], scale)
        for a, b in itertools.combinations(targets.values(), 2)
    )
    sources = sorted(Path("experiments/ibex_temporal_v1").glob("*.py"))
    sources += [Path("src/agcws/policies/vertex.py"), Path("docker/run.sh")]
    binary = (
        root
        / "toolchain/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system"
    )
    image = subprocess.check_output(
        [
            "docker",
            "image",
            "inspect",
            "agcws:window-validation-v1",
            "--format",
            "{{.Id}}",
        ],
        text=True,
    ).strip()
    measurement = {
        "binary_sha256": file_sha256(binary),
        "image_id": image,
        "ibex_commit": subprocess.check_output(
            ["git", "-C", "third_party/ibex", "rev-parse", "HEAD"], text=True
        ).strip(),
        "configuration": "simple_system defaults, RV32MFast, ICache=0, MHPMCounterNum=12",
    }
    manifest = {
        "phase": "development-only",
        "targets": targets,
        "scale": scale,
        "tolerance": min(0.10, separation / 3),
        "minimum_target_separation": separation,
        "tolerance_rule": "min(0.10, minimum pairwise witness normalized RMSE / 3)",
        "seeds": [600, 601, 602],
        "budget": 16,
        "batch_size": 2,
        "shared_initial_slots": 2,
        "policies": ["random", "mutation", "agent"],
        "measurement": measurement,
        "model": os.environ["AGCWS_GEMINI_MODEL"],
        "input_rate": 0.30,
        "output_rate": 2.50,
        "pricing_units": "estimated USD per million input/output tokens, includes thinking output",
        "temperature": 0.7,
        "top_p": 0.95,
        "thinking_budget": 512,
        "max_output_tokens": 8192,
        "transport": "120s HTTP deadline; no process alarm; one attempt, no free repair",
        "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
        "sources": {str(p): file_sha256(p) for p in sources},
    }
    if manifest["model"] != "gemini-2.5-flash":
        raise ValueError(
            "this development pricing/configuration is for gemini-2.5-flash"
        )
    manifest["measurement_fingerprint"] = key(
        {"measurement": measurement, "sources": manifest["sources"]}
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as output:
        output.write(json.dumps(manifest, indent=2) + "\n")
    print(destination, manifest["tolerance"], separation, flush=True)


def panel(root, manifest_path, workers):
    manifest = json.loads(manifest_path.read_text())
    cells = list(
        itertools.product(manifest["targets"], manifest["seeds"], manifest["policies"])
    )
    logs = root / "panel-logs"
    logs.mkdir(exist_ok=True)

    def run(cell):
        target, seed, policy = cell
        directory = root / "panel" / target / f"seed-{seed}" / policy
        if (directory / "summary.json").exists():
            return {"cell": cell, "status": "already complete"}
        if directory.exists():
            return {"cell": cell, "status": "incomplete; inspect, do not overwrite"}
        with (logs / f"{target}-{seed}-{policy}.log").open("w") as log:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "experiments.ibex_temporal_v1.search",
                    "--root",
                    str(root),
                    "--manifest",
                    str(manifest_path),
                    "--target",
                    target,
                    "--seed",
                    str(seed),
                    "--policy",
                    policy,
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        record = {
            "cell": cell,
            "returncode": result.returncode,
            "complete": (directory / "summary.json").exists(),
        }
        print(json.dumps(record), flush=True)
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        records = list(pool.map(run, cells))
    (root / "panel-status.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "run"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.manifest)
    else:
        panel(args.root, args.manifest, args.workers)
