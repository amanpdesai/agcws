"""Eight-slot CPU qualification and independent compact-evidence replay."""

import argparse
import fcntl
import gzip
import os
import subprocess
from pathlib import Path

from agcws.provenance import file_sha256
from analysis.ibex_depth_v1 import check_trial
from analysis.temporal_scaling_v1 import check_loss
from experiments.gest_bridge_v1.bridge import HASHES, Bridge, upstream
from experiments.ibex_capability_v1.study import BINARY
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_depth_v1.study import evaluate
from experiments.ibex_temporal_v3.search import verify_runtime
from experiments.temporal_scaling_v1.smoke import EVIDENCE


def freeze(root, archive, runtime):
    parent = read(Path("results/ibex_temporal_v4_development/manifest.json"))
    verify_runtime(parent, runtime)
    upstream()
    target_path = Path("results/temporal_scaling_v1/targets.json")
    target = read(target_path)[0]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    names = (
        set(parent["sources"])
        | {
            str(p)
            for folder in (
                "experiments/gest_bridge_v1",
                "experiments/ibex_depth_v1",
                "experiments/temporal_scaling_v1",
            )
            for p in Path(folder).glob("*.py")
        }
        | {
            "experiments/ibex_capability_v1/study.py",
            "docs/GEST_BRIDGE_V1.md",
            "analysis/ibex_depth_v1.py",
            "analysis/temporal_scaling_v1.py",
        }
    )
    sources = {}
    for name in sorted(names):
        if (
            subprocess.check_output(["git", "show", f"{commit}:{name}"])
            != Path(name).read_bytes()
        ):
            raise ValueError(f"uncommitted producer: {name}")
        sources[name] = file_sha256(Path(name))
    root.mkdir(parents=True, exist_ok=False)
    archive.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    os.link(runtime / BINARY, root / BINARY)
    write(archive / "parent_manifest.json", parent)
    write(
        archive / "manifest.json",
        {
            "phase": "CPU-only qualification, not efficacy study",
            "seed": 840,
            "budget": 8,
            "batch_size": 2,
            "source_commit": commit,
            "sources": sources,
            "upstream_sha256": HASHES,
            "measurement_fingerprint": parent["measurement_fingerprint"],
            "scale": parent["scale"],
            "tolerance": parent["tolerance"],
            "target_rates": target["target_rates"],
            "target_source": str(target_path),
            "target_source_sha256": file_sha256(target_path),
            "target_index": 0,
        },
    )


def identity(archive):
    manifest = read(archive / "manifest.json")
    upstream()
    if manifest["upstream_sha256"] != HASHES:
        raise ValueError("upstream manifest differs")
    for name, digest in manifest["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"source differs: {name}")
    target_path = Path(manifest["target_source"])
    if file_sha256(target_path) != manifest["target_source_sha256"]:
        raise ValueError("witness source differs")
    if (
        read(target_path)[manifest["target_index"]]["target_rates"]
        != manifest["target_rates"]
    ):
        raise ValueError("witness rates differ")
    return manifest


def run(root, archive):
    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest = identity(archive)
        for name in ("manifest.json", "parent_manifest.json"):
            path = archive / name
            if (
                subprocess.check_output(["git", "show", f"HEAD:{path}"])
                != path.read_bytes()
            ):
                raise ValueError("commit manifests before execution")
        verify_runtime(read(archive / "parent_manifest.json"), root)
        bridge = Bridge(manifest["seed"], manifest["budget"])
        history = []
        while bridge.used < bridge.budget:
            proposals = bridge.ask()
            batch_path = root / "batches" / f"{proposals[0]['slot']:03}.json"
            ensure(batch_path, proposals)
            batch = []
            for proposal in proposals:
                path = root / "trials" / f"{proposal['slot']:03}.json"
                if path.exists():
                    trial = read(path)
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
                        "gest-phase-adaptation-v1",
                    )
                    trial["operator"] = proposal["operator"]
                    trial["parents"] = proposal["parents"]
                    write(path, trial)
                if any(
                    trial[k] != proposal[k]
                    for k in ("program", "slot", "operator", "parents")
                ):
                    raise ValueError("resume proposal differs")
                batch.append(trial)
                print(
                    f"slot={trial['slot']} valid={trial['valid']} stage={trial['stage']}",
                    flush=True,
                )
            bridge.tell(batch)
            history.extend(batch)
        ensure(archive / "trials.json", history)
        for identifier in sorted({t["cache_id"] for t in history if t["cache_id"]}):
            for name in EVIDENCE:
                source = root / "cache" / identifier / name
                if not source.exists():
                    continue
                target = archive / "evaluations" / identifier / (name + ".gz")
                target.parent.mkdir(parents=True, exist_ok=True)
                data = gzip.compress(source.read_bytes(), mtime=0)
                if target.exists():
                    if target.read_bytes() != data:
                        raise ValueError("existing evidence differs")
                else:
                    with target.open("xb") as stream:
                        stream.write(data)
        summary = audit(archive)
        ensure(archive / "summary.json", summary)
        ensure(root / "complete.json", summary)
        print(summary, flush=True)


def audit(archive):
    manifest = identity(archive)
    trials = read(archive / "trials.json")
    if len(trials) != manifest["budget"]:
        raise ValueError("incomplete trajectory")
    bridge = Bridge(manifest["seed"], manifest["budget"])
    for offset in range(0, len(trials), 2):
        batch = trials[offset : offset + 2]
        for proposal, trial in zip(bridge.ask(), batch, strict=True):
            if any(
                trial[k] != proposal[k]
                for k in ("program", "slot", "operator", "parents")
            ):
                raise ValueError("proposal reconstruction differs")
            check_trial(archive, trial, manifest)
            check_loss(trial, manifest["target_rates"], manifest["scale"])
        bridge.tell(batch)
    valid = [t for t in trials if t["valid"]]
    summary = {
        "complete": True,
        "proposals": len(trials),
        "valid": len(valid),
        "upstream_operator_slots": sum(t["operator"] != "bootstrap" for t in trials),
        "cache_hits": sum(t["cache_hit"] for t in trials),
        "best_error": min((t["loss"] for t in valid), default=None),
        "model_calls": 0,
        "claim": "component and CPU integration qualification only",
    }
    if (archive / "summary.json").exists() and read(
        archive / "summary.json"
    ) != summary:
        raise ValueError("summary differs")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run", "audit"))
    parser.add_argument("--root", type=Path, default=Path("out/gest-bridge-v1"))
    parser.add_argument("--archive", type=Path, default=Path("results/gest_bridge_v1"))
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
