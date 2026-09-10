"""Frozen twelve-proposal screening smoke with measured-only evidence auditing."""

import argparse
import fcntl
import gzip
import json
import os
import subprocess
from pathlib import Path

import numpy as np

from agcws.provenance import file_sha256
from analysis.ibex_depth_v1 import check_trial
from analysis.temporal_scaling_v1 import check_loss
from experiments.gest_bridge_v1.qualification import identity
from experiments.ibex_capability_v1.study import BINARY
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_depth_v1.study import evaluate
from experiments.ibex_temporal_v3.search import verify_runtime
from experiments.saga_temporal_v1.policy import Policy
from experiments.temporal_scaling_v1.smoke import EVIDENCE


def freeze(root, archive, runtime):
    previous = Path("results/gest_bridge_v1")
    source = identity(previous)
    parent = read(previous / "parent_manifest.json")
    verify_runtime(parent, runtime)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    names = (
        set(source["sources"])
        | {str(p) for p in Path("experiments/saga_temporal_v1").glob("*.py")}
        | {"docs/SAGA_TEMPORAL_V1.md"}
    )
    sources = {}
    for name in sorted(names):
        if (
            subprocess.check_output(["git", "show", f"{commit}:{name}"])
            != Path(name).read_bytes()
        ):
            raise ValueError(f"uncommitted source: {name}")
        sources[name] = file_sha256(Path(name))
    probe = json.loads(
        subprocess.check_output(
            [
                "uv",
                "run",
                "--isolated",
                "--no-project",
                "--python",
                "3.12",
                "--with",
                "numpy==2.4.2",
                "--with",
                "scipy==1.17.1",
                "python",
                "experiments/saga_temporal_v1/upstream_probe.py",
            ],
            text=True,
        )
    )
    root.mkdir(parents=True, exist_ok=False)
    archive.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    os.link(runtime / BINARY, root / BINARY)
    write(archive / "parent_manifest.json", parent)
    write(archive / "upstream_probe.json", probe)
    write(
        archive / "manifest.json",
        {
            **source,
            "phase": "SAGA-inspired ridge screening qualification, not reproduction",
            "seed": 850,
            "budget": 12,
            "batch_size": 4,
            "bootstrap_measured": 4,
            "selected_per_screened_batch": 2,
            "ridge_alpha": 1.0,
            "source_commit": commit,
            "sources": sources,
            "numpy_version": np.__version__,
            "parent_sha256": file_sha256(archive / "parent_manifest.json"),
            "probe_sha256": file_sha256(archive / "upstream_probe.json"),
            "upstream_predictor_sha256": probe["predictor_sha256"],
        },
    )


def check_identity(archive):
    manifest = identity(archive)
    if np.__version__ != manifest["numpy_version"]:
        raise ValueError("numerical dependency differs")
    for name, key in (
        ("parent_manifest.json", "parent_sha256"),
        ("upstream_probe.json", "probe_sha256"),
    ):
        if file_sha256(archive / name) != manifest[key]:
            raise ValueError(f"changed {name}")
    if (
        file_sha256(Path("third_party/gest_saga/src/PredictReferenceFeatures.py"))
        != manifest["upstream_predictor_sha256"]
    ):
        raise ValueError("upstream predictor differs")
    return manifest


def run(root, archive):
    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = check_identity(archive)
        for name in ("manifest.json", "parent_manifest.json", "upstream_probe.json"):
            path = archive / name
            if (
                subprocess.check_output(["git", "show", f"HEAD:{path}"])
                != path.read_bytes()
            ):
                raise ValueError("commit qualification inputs before execution")
        verify_runtime(read(archive / "parent_manifest.json"), root)
        policy = Policy(
            manifest["seed"],
            manifest["budget"],
            manifest["target_rates"],
            manifest["scale"],
        )
        history, decisions = [], []
        while policy.used < policy.budget:
            try:
                request = policy.ask()
            except (ValueError, np.linalg.LinAlgError) as exc:
                ensure(
                    root / "qualification_failure.json",
                    {
                        "error": str(exc),
                        "charged_proposals": policy.used,
                        "pending_proposals": [p for _, p in policy._pending],
                    },
                )
                raise
            ensure(root / "batches" / f"{policy.used:03}.json", request)
            decisions.append(request)
            batch = []
            for proposal in request["proposals"]:
                path = root / "trials" / f"{proposal['slot']:03}.json"
                if path.exists():
                    trial = read(path)
                elif not proposal["selected"]:
                    trial = {
                        **proposal,
                        "status": "FILTERED",
                        "valid": None,
                        "rates": None,
                        "loss": None,
                    }
                    write(path, trial)
                else:
                    trial = evaluate(
                        {
                            "submitted": proposal["program"],
                            "prediction": None,
                            "prediction_error": None,
                        },
                        proposal["slot"],
                        history,
                        manifest,
                        root,
                        "temporal-ridge-screen-v1",
                    )
                    trial.update(
                        parents=proposal["parents"], selected=True, status="MEASURED"
                    )
                    write(path, trial)
                batch.append(trial)
                print(
                    f"slot={trial['slot']} status={trial['status']} valid={trial['valid']}",
                    flush=True,
                )
            policy.tell(batch)
            history.extend(batch)
        ensure(archive / "trials.json", history)
        ensure(archive / "decisions.json", decisions)
        for identifier in sorted({t["cache_id"] for t in history if t.get("cache_id")}):
            for name in EVIDENCE:
                source = root / "cache" / identifier / name
                if not source.exists():
                    continue
                destination = archive / "evaluations" / identifier / (name + ".gz")
                destination.parent.mkdir(parents=True, exist_ok=True)
                data = gzip.compress(source.read_bytes(), mtime=0)
                if destination.exists():
                    if destination.read_bytes() != data:
                        raise ValueError("archived evidence differs")
                else:
                    with destination.open("xb") as stream:
                        stream.write(data)
        summary = audit(archive)
        ensure(archive / "summary.json", summary)
        ensure(root / "complete.json", summary)
        print(summary, flush=True)


def audit(archive):
    manifest = check_identity(archive)
    history, decisions = read(archive / "trials.json"), read(archive / "decisions.json")
    if len(history) != manifest["budget"] or len(decisions) * 4 != len(history):
        raise ValueError("incomplete qualification")
    policy = Policy(
        manifest["seed"],
        manifest["budget"],
        manifest["target_rates"],
        manifest["scale"],
    )
    for offset in range(0, len(history), 4):
        actual = policy.ask()
        recorded = decisions[offset // 4]
        if actual != recorded:
            raise ValueError("proposal or pre-measurement selection differs")
        batch = history[offset : offset + 4]
        for trial in batch:
            if trial["status"] == "MEASURED":
                check_trial(archive, trial, manifest)
                check_loss(trial, manifest["target_rates"], manifest["scale"])
        policy.tell(batch)
    measured = [t for t in history if t["status"] == "MEASURED"]
    valid = [t for t in measured if t["valid"]]
    summary = {
        "complete": True,
        "proposals": len(history),
        "selected_evaluations": len(measured),
        "filtered_unknown_validity": len(history) - len(measured),
        "valid_measured": len(valid),
        "cache_hits": sum(t["cache_hit"] for t in measured),
        "simulator_executions": sum(
            bool(t["cache_id"]) and not t["cache_hit"] for t in measured
        ),
        "best_measured_error": min((t["loss"] for t in valid), default=None),
        "model_calls": 0,
        "claim": "screening integration only; filtered outcomes unmeasured",
    }
    if (archive / "summary.json").exists() and read(
        archive / "summary.json"
    ) != summary:
        raise ValueError("summary differs")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run", "audit"))
    parser.add_argument("--root", type=Path, default=Path("out/saga-temporal-v1"))
    parser.add_argument(
        "--archive", type=Path, default=Path("results/saga_temporal_v1")
    )
    parser.add_argument("--runtime", type=Path, default=Path("out/temporal-scaling-v1"))
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.archive, args.runtime)
    elif args.action == "run":
        run(args.root, args.archive)
    else:
        print(audit(args.archive))


if __name__ == "__main__":
    main()
