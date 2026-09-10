"""Immutable construction and closed-loop execution; no policy fallbacks."""

import argparse
import concurrent.futures
import fcntl
import gzip
import json
import os
import random
import subprocess
import threading
import time
from pathlib import Path

from agcws import config
from agcws.provenance import file_sha256
from experiments.baseline_panel_v1.policies import witness_program
from experiments.baseline_panel_v1.study import archive_evaluations, committed, record
from experiments.ibex_capability_v1.study import BINARY
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.model import settings
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_depth_v1.study import Meter, evaluate
from experiments.ibex_temporal_v3.program import random_program
from experiments.ibex_temporal_v3.search import verify_runtime
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.grounded_agent import payload
from experiments.ibex_temporal_v4.native_schema import serving_schema
from experiments.nonflat_temporal_v1.targets import select
from experiments.temporal_scaling_v1.baselines import phase_random

ROOT = Path("out/nonflat-temporal-v1")
ARCHIVE = Path("results/nonflat_temporal_v1")
SEEDS = list(range(1200, 1206))
ARMS = ["phase-random", "pro-4096"]
ARCHIVE_LOCK = threading.Lock()


def freeze(root, archive, runtime):
    previous = read(Path("results/baseline_panel_v1/manifest.json"))
    depth = read(Path("results/ibex_depth_v1/manifest.json"))
    parent = read(Path("results/ibex_depth_v1/parent_manifest.json"))
    for ancestor in (previous, depth):
        for name, digest in ancestor["sources"].items():
            if file_sha256(Path(name)) != digest:
                raise ValueError(f"ancestor source changed: {name}")
    verify_runtime(parent, runtime)
    names = (
        set(previous["sources"])
        | set(depth["sources"])
        | {str(p) for p in Path("experiments/nonflat_temporal_v1").glob("*.py")}
        | {"docs/NONFLAT_TEMPORAL_V1_PROTOCOL.md"}
    )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    sources = {}
    for name in sorted(names):
        committed(Path(name))
        sources[name] = file_sha256(Path(name))
    root.mkdir(parents=True, exist_ok=False)
    archive.mkdir(parents=True, exist_ok=False)
    (root / BINARY).parent.mkdir(parents=True)
    os.link(runtime / BINARY, root / BINARY)
    write(archive / "parent_manifest.json", parent)
    write(archive / "schema.json", serving_schema(2, True))
    write(
        archive / "manifest.json",
        {
            "phase": "non-flat fresh-target confirmation",
            "source_commit": commit,
            "sources": sources,
            "parent_sha256": file_sha256(archive / "parent_manifest.json"),
            "schema_sha256": file_sha256(archive / "schema.json"),
            "measurement_fingerprint": depth["measurement_fingerprint"],
            "scale": depth["scale"],
            "tolerance": depth["tolerance"],
            "construction_seed": 1100,
            "construction_count": 24,
            "minimum_constant_floor": 0.20,
            "minimum_pair_distance": 0.15,
            "target_count": 3,
            "seeds": SEEDS,
            "arms": ARMS,
            "budget": 128,
            "smoke_seed": 1190,
            "smoke_budget": 4,
            "maximum_workers": 4,
            "models": {"pro-4096": settings("pro-4096")},
            "ceiling_usd": 150,
            "payload_bound": 200000,
            "funding_authority": "User confirmed additional GCP funding and authorized launch on 2026-09-10",
            "pricing_checked_utc": "2026-09-10",
            "pricing_source": "https://cloud.google.com/vertex-ai/generative-ai/pricing",
        },
    )


def identity(archive):
    m = read(archive / "manifest.json")
    for name, digest in m["sources"].items():
        if file_sha256(Path(name)) != digest:
            raise ValueError(f"frozen source changed: {name}")
    for name in ("parent", "schema"):
        filename = "parent_manifest.json" if name == "parent" else "schema.json"
        if file_sha256(archive / filename) != m[f"{name}_sha256"]:
            raise ValueError(f"{name} identity changed")
    if settings("pro-4096") != m["models"]["pro-4096"]:
        raise ValueError("model settings changed")
    return m


def selected(witnesses, m):
    return select(
        witnesses,
        m["scale"],
        m["target_count"],
        m["minimum_constant_floor"],
        m["minimum_pair_distance"],
    )


def construct(root, archive, m):
    rng = random.Random(m["construction_seed"])
    proposals = [
        {
            "slot": i,
            "program": witness_program("scheduled-four-phase", rng, i),
            "selected": True,
            "parents": [],
            "constructor": "scheduled-four-phase",
        }
        for i in range(1, m["construction_count"] + 1)
    ]
    ensure(root / "construction_proposals.json", proposals)
    local = {**m, "target_rates": [0.0] * 8}

    def one(p):
        t = record(root, root / "construction" / f"{p['slot']:03}.json", p, [], local)
        print(
            json.dumps({"construction_slot": p["slot"], "valid": t["valid"]}),
            flush=True,
        )
        return t

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        trials = list(pool.map(one, proposals))
    ensure(archive / "witnesses.json", trials)
    archive_evaluations(root, archive, trials)
    from experiments.nonflat_temporal_v1.audit import check_witnesses

    check_witnesses(archive, m, trials)
    try:
        targets = selected(trials, m)
    except ValueError as exc:
        ensure(archive / "qualification_failure.json", {"reason": str(exc)})
        raise
    ensure(archive / "targets.json", targets)
    print(
        json.dumps({"qualified_targets": len(targets), "commit_before_search": True}),
        flush=True,
    )


def cpu_candidates(rng, offset):
    if offset == 0:
        return [random_program(rng) for _ in range(2)]
    return [phase_random(rng, offset + j + 1) for j in range(2)]


def search(root, archive, m, target, seed, arm, budget, meter, section="panel"):
    cell = {"target": target["id"], "seed": seed, "arm": arm}
    directory = root / section / target["id"] / str(seed) / arm
    digest = file_sha256(archive / "search_manifest.json")
    ensure(directory / "identity.json", {"cell": cell, "search_sha256": digest})
    local = {**m, "target_rates": target["rates"]}
    rng, history = random.Random(seed), []
    for offset in range(0, budget, 2):
        if meter.halted.is_set():
            raise RuntimeError("study halted; checkpoints retained")
        model_batch = arm == "pro-4096" and offset > 0
        candidates = None if model_batch else cpu_candidates(rng, offset)
        contents = (
            payload(
                history,
                {
                    "profile": target["rates"],
                    "scale": m["scale"],
                    "tolerance": m["tolerance"],
                },
                2,
                True,
            )
            if model_batch
            else None
        )
        batch = directory / "batches" / f"{offset + 1:03}"
        ident = {"cell": cell, "first_slot": offset + 1, "search_sha256": digest}
        ensure(
            batch / "input.json",
            {"identity": ident, "payload": contents, "cpu_candidates": candidates},
        )
        response = None
        if model_batch:
            schema = read(archive / "schema.json")
            if (
                len(contents.encode()) + len(json.dumps(schema).encode()) + 4096
                > m["payload_bound"]
            ):
                raise RuntimeError("payload exceeds frozen bound; no truncation")
            response = meter.call(batch, arm, contents, schema, ident)
            if (
                not response.get("api_error")
                and response["model_version"] != m["models"][arm]["model"]
            ):
                raise RuntimeError("model identity changed; response retained")
            decoded = decode(response["raw_text"], 2, True)
        else:
            decoded = decode(
                json.dumps({"hypothesis": "CPU proposal", "candidates": candidates}), 2
            )
        ensure(batch / "decoded.json", decoded)
        if (batch / "trials.json").exists():
            trials = read(batch / "trials.json")
            if len(trials) != 2 or any(
                t["slot"] != offset + j + 1
                or t["program"] != decoded["slots"][j]["submitted"]
                for j, t in enumerate(trials)
            ):
                raise ValueError("saved trials differ from proposals")
        else:
            trials = [
                evaluate(
                    p,
                    offset + j + 1,
                    history,
                    local,
                    root,
                    "initial" if offset == 0 else arm,
                )
                for j, p in enumerate(decoded["slots"])
            ]
            if response and response.get("api_error"):
                for trial in trials:
                    trial.update(stage="API", reason=response["api_error"]["message"])
            write(batch / "trials.json", trials)
        history.extend(trials)
        print(
            json.dumps({"progress": cell, "completed_slots": len(history)}), flush=True
        )
    result = {
        "cell": cell,
        "trials": history,
        "prefixes": {
            str(n): summarize(history, n, m["tolerance"])
            for n in (16, 64, 128)
            if n <= budget
        },
    }
    ensure(directory / "complete.json", result)
    with ARCHIVE_LOCK:
        archive_evaluations(root, archive, history)
        destination = archive / section / target["id"] / str(seed) / arm
        for source in sorted((directory / "batches").glob("*/*.json")):
            saved = destination / source.relative_to(directory)
            saved = Path(str(saved) + ".gz")
            saved.parent.mkdir(parents=True, exist_ok=True)
            data = gzip.compress(source.read_bytes(), mtime=0)
            if saved.exists():
                if saved.read_bytes() != data:
                    raise ValueError("archived batch changed")
            else:
                with saved.open("xb") as stream:
                    stream.write(data)
        ensure(destination / "complete.json", result)
    return result


def freeze_search(archive, m):
    committed(archive / "targets.json")
    targets = read(archive / "targets.json")
    if targets != selected(read(archive / "witnesses.json"), m):
        raise ValueError("target selection differs")
    ensure(
        archive / "search_manifest.json",
        {
            "manifest_sha256": file_sha256(archive / "manifest.json"),
            "targets_sha256": file_sha256(archive / "targets.json"),
            "cells": [
                {"target": t["id"], "seed": s, "arm": a}
                for t in targets
                for s in m["seeds"]
                for a in m["arms"]
            ],
        },
    )


def run(root, archive, m, smoke=False):
    search_manifest = read(archive / "search_manifest.json")
    for name in ("manifest", "targets"):
        if file_sha256(archive / f"{name}.json") != search_manifest[f"{name}_sha256"]:
            raise ValueError("search input changed")
    committed(archive / "search_manifest.json")
    targets = {t["id"]: t for t in read(archive / "targets.json")}
    config._load_dotenv()
    meter = Meter(root, m["ceiling_usd"])
    if smoke:
        result = search(
            root,
            archive,
            m,
            next(iter(targets.values())),
            m["smoke_seed"],
            "phase-random",
            m["smoke_budget"],
            meter,
            "smoke",
        )
        from experiments.nonflat_temporal_v1.audit import check_cell

        check_cell(archive, m, result, m["smoke_budget"])
        ensure(
            archive / "smoke_pass.json",
            {
                "slots": m["smoke_budget"],
                "model_calls": 0,
                "search_sha256": file_sha256(archive / "search_manifest.json"),
            },
        )
        return
    committed(archive / "smoke_pass.json")
    if read(archive / "smoke_pass.json")["search_sha256"] != file_sha256(
        archive / "search_manifest.json"
    ):
        raise ValueError("smoke belongs to different search")
    ensure(
        root / "launch.json",
        {
            "search_sha256": file_sha256(archive / "search_manifest.json"),
            "cells": len(search_manifest["cells"]),
            "cap_usd": meter.ceiling,
        },
    )
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=m["maximum_workers"]
    ) as pool:
        futures = [
            pool.submit(
                search,
                root,
                archive,
                m,
                targets[c["target"]],
                c["seed"],
                c["arm"],
                m["budget"],
                meter,
            )
            for c in search_manifest["cells"]
        ]
        try:
            for future in concurrent.futures.as_completed(futures):
                future.result()
        except Exception:
            meter.halted.set()
            for future in futures:
                future.cancel()
            raise
    from experiments.nonflat_temporal_v1.audit import audit

    ensure(archive / "summary.json", audit(archive))
    ensure(
        root / "complete.json",
        {
            "cells": len(search_manifest["cells"]),
            "slots": len(search_manifest["cells"]) * m["budget"],
        },
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=("freeze", "construct", "freeze-search", "smoke", "run", "audit"),
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--runtime", type=Path, default=Path("out/temporal-scaling-v1"))
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root, args.archive, args.runtime)
        return
    m = identity(args.archive)
    if args.action == "audit":
        from experiments.nonflat_temporal_v1.audit import audit

        print(audit(args.archive))
        return
    committed(args.archive / "manifest.json")
    verify_runtime(read(args.archive / "parent_manifest.json"), args.root)
    with (args.root / "runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            if args.action == "construct":
                construct(args.root, args.archive, m)
            elif args.action == "freeze-search":
                freeze_search(args.archive, m)
            else:
                run(args.root, args.archive, m, smoke=args.action == "smoke")
        except Exception as exc:
            write(
                args.root / f"failure-{time.time_ns()}.json",
                {"action": args.action, "error": repr(exc), "pid": os.getpid()},
            )
            raise


if __name__ == "__main__":
    main()
