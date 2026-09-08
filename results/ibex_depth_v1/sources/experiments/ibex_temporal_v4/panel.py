"""Freeze and supervise the four-arm grounded temporal development panel."""

import argparse
import concurrent.futures
import itertools
import json
import subprocess
import sys
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v3.search import key, verify_runtime
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.contract_study import digest
from experiments.ibex_temporal_v4.search import POLICIES


def freeze(root, destination):
    previous_path = Path("results/ibex_temporal_v3_development/manifest.json")
    manifest = json.loads(previous_path.read_text())
    for name in tuple(manifest):
        if name.startswith("context") or name in ("prompts", "gate_sha256"):
            manifest.pop(name)
    rtl_commit = subprocess.check_output(
        ["git", "-C", "third_party/ibex", "rev-parse", "HEAD"], text=True
    ).strip()
    rtl_dirty = subprocess.check_output(
        ["git", "-C", "third_party/ibex", "status", "--porcelain"], text=True
    ).strip()
    if rtl_dirty or rtl_commit != manifest["measurement"]["ibex_commit"]:
        raise ValueError("RTL differs from pinned simulator configuration")
    prediction_path = Path("results/ibex_temporal_v4_prediction_gate/result.json")
    prediction = json.loads(prediction_path.read_text())
    decoded = decode(prediction["raw_text"], 2, True)
    if (
        not prediction["ready"]
        or prediction["usage_unknown"]
        or decoded != prediction["decoded"]
        or decoded["response_error"] is not None
        or any(
            s["canonical"] is None or s["prediction"]["reference_slot"] != 1
            for s in decoded["slots"]
        )
    ):
        raise ValueError("prediction gate has not passed")
    from analysis.ibex_contract_v4 import verify as verify_contract

    if not verify_contract(Path("results/ibex_temporal_v4_contract_v2"))["ready"]:
        raise ValueError("response contract gate has not passed")
    gates = {}
    for name in ("ibex_temporal_v4_gate", "ibex_temporal_v4_gate_tiny"):
        directory = Path("results") / name
        gate = json.loads((directory / "gate.json").read_text())
        if not all(
            gate[k]
            for k in (
                "loadable_bytes_identical",
                "architectural_state_identical",
                "activity_identical",
            )
        ):
            raise ValueError("CPU equivalence gate failed")
        for path, expected in gate["evidence"].items():
            if file_sha256(directory / path) != expected:
                raise ValueError("CPU gate evidence changed")
        gates[str(directory / "gate.json")] = file_sha256(directory / "gate.json")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    files = {Path(p) for p in manifest["sources"]} | set(
        Path("experiments/ibex_temporal_v4").glob("*.py")
    )
    files.update(
        Path(p)
        for p in (
            "docs/IBEX_TEMPORAL_V4_PLAN.md",
            "docs/IBEX_CONTRACT_V4_REVISION2.md",
            "docs/IBEX_V4_PREDICTION_GATE.md",
        )
    )
    sources = {}
    for p in sorted(files):
        if digest(
            subprocess.check_output(["git", "show", f"{commit}:{p}"])
        ) != file_sha256(p):
            raise ValueError(f"uncommitted source: {p}")
        sources[str(p)] = file_sha256(p)
    manifest.update(
        sources=sources,
        policies=list(POLICIES),
        source_commit=commit,
        previous_manifest_sha256=file_sha256(previous_path),
        prediction_gate_sha256=file_sha256(prediction_path),
        cpu_gates=gates,
        neutral_band=0.01,
        notebook_limit=6,
        phase="grounded-temporal-development",
        version="v4",
        budget=16,
    )
    manifest["measurement_fingerprint"] = key(
        {"measurement": manifest["measurement"], "sources": sources}
    )
    verify_runtime(manifest, root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")


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
                    "experiments.ibex_temporal_v4.search",
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
    parser.add_argument("action", choices=("freeze", "run"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.manifest)
    else:
        panel(args.root, args.manifest, args.workers)
