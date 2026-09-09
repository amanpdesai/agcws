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
from experiments.ibex_temporal_v3.search import POLICIES, key


def freeze(root, destination):
    from importlib.metadata import version
    from experiments.ibex_temporal_v3.agent import prompt
    from experiments.ibex_temporal_v3.context import EXCERPTS, CHAR_BUDGET, load_context

    config._load_dotenv()
    old_path = Path("results/ibex_proposal_v2_development/manifest.json")
    old = json.loads(old_path.read_text())
    gate = json.loads((root / "gate.json").read_text())
    if not gate["numeric_equivalence"] or not gate["same_activity_window"]:
        raise ValueError("numeric/feedback gate has not passed")
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
    if (
        file_sha256(binary) != old["measurement"]["binary_sha256"]
        or image != old["measurement"]["image_id"]
    ):
        raise ValueError("simulator/image differs from v2")
    commit = subprocess.check_output(
        ["git", "-C", "third_party/ibex", "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "-C", "third_party/ibex", "status", "--porcelain"], text=True
    ).strip()
    if dirty or commit != old["measurement"]["ibex_commit"]:
        raise ValueError("RTL source differs from the pinned simulator configuration")
    context_root = Path("out/ibex-source-context-v3")
    context_hash = file_sha256(context_root / "manifest.json")
    context = load_context(context_root, context_hash)
    sources = []
    for generation in ("v1", "v2", "v3"):
        sources += sorted(Path(f"experiments/ibex_temporal_{generation}").glob("*.py"))
    sources += [
        Path(p)
        for p in (
            "src/agcws/policies/vertex.py",
            "src/agcws/policies/source_context.py",
            "src/agcws/provenance.py",
            "src/agcws/config.py",
            "docker/run.sh",
            "scripts/build_ibex_context.py",
            "specs/ibex.md",
            "docs/IBEX_TEMPORAL_V3_DEVELOPMENT.md",
        )
    ]
    manifest = {
        **{
            k: old[k]
            for k in (
                "targets",
                "scale",
                "tolerance",
                "minimum_target_separation",
                "tolerance_rule",
                "seeds",
                "budget",
                "batch_size",
                "shared_initial_slots",
                "measurement",
                "model",
                "input_rate",
                "output_rate",
                "pricing_units",
                "temperature",
                "top_p",
                "thinking_budget",
                "max_output_tokens",
                "transport",
            )
        },
        "phase": "development-only",
        "version": "temporal-context-correction-v3",
        "v2_manifest_sha256": file_sha256(old_path),
        "gate_sha256": file_sha256(root / "gate.json"),
        "policies": list(POLICIES),
        "prompts": {
            policy: hashlib.sha256(
                prompt(
                    policy in ("agent-context", "agent-combined"),
                    policy in ("agent-correction", "agent-combined"),
                ).encode()
            ).hexdigest()
            for policy in POLICIES
        },
        "context_root": str(context_root),
        "context_sha256": context_hash,
        "context_excerpts": EXCERPTS,
        "context_char_budget": CHAR_BUDGET,
        "context_payload_sha256": key(context),
        "descriptor": "eight retirement-gap quartiles plus dominant alu/multiply/divide/load/store class",
        "coverage_restart_probability": 0.2,
        "coverage_parent_rule": "uniform among least-visited occupied cells; retain lowest-loss elite",
        "sources": {str(p): file_sha256(p) for p in sources},
        "packages": {name: version(name) for name in ("google-genai", "jsonschema")},
    }
    if os.environ["AGCWS_GEMINI_MODEL"] != manifest["model"]:
        raise ValueError("configured model differs from declared Flash control")
    manifest["measurement_fingerprint"] = key(
        {
            "measurement": manifest["measurement"],
            "sources": manifest["sources"],
        }
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as output:
        output.write(json.dumps(manifest, indent=2) + "\n")
    print(
        destination,
        len(POLICIES) * len(manifest["targets"]) * len(manifest["seeds"]),
        flush=True,
    )


def panel(root, manifest_path, workers):
    if workers < 1:
        raise ValueError("positive worker count required")
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
                    "experiments.ibex_temporal_v3.search",
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
    if any(
        not r.get("complete", r.get("status") == "already complete") for r in records
    ):
        raise RuntimeError(
            "panel incomplete; inspect status and logs without overwriting"
        )


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
