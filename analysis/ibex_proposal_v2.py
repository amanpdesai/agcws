"""Archive the versioned allocation diagnostic without changing the v1 results."""

import argparse
import collections
import json
import shutil
from pathlib import Path

from agcws.provenance import file_sha256
from analysis.ibex_expressiveness import archive as base_archive
from analysis.ibex_expressiveness import verify as base_verify


def has_integral_float(value):
    if isinstance(value, dict):
        return any(has_integral_float(v) for v in value.values())
    if isinstance(value, list):
        return any(has_integral_float(v) for v in value)
    return isinstance(value, float) and value.is_integer()


def readiness(destination):
    manifest = json.loads((destination / "manifest.json").read_text())
    generated = []
    for path in sorted(destination.glob("panel/*/*/agent/trials.jsonl")):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        generated.extend(
            row for row in rows if row["slot"] > manifest["shared_initial_slots"]
        )
    expected = (
        len(manifest["targets"])
        * len(manifest["seeds"])
        * (manifest["budget"] - manifest["shared_initial_slots"])
    )
    if len(generated) != expected:
        raise ValueError("incomplete model-generated proposal panel")
    counts = collections.Counter(
        "VALID" if row["valid"] else row["stage"] for row in generated
    )
    fraction = counts["VALID"] / expected
    work_rejections = sum(
        row["stage"] == "PROTOCOL" and "4096" in row["reason"] for row in generated
    )
    threshold = manifest["readiness"]
    return {
        "scope": "observed development targets; proposal readiness, not superiority",
        "model_generated_slots": expected,
        "model_generated_validity": dict(counts),
        "model_generated_valid_fraction": fraction,
        "work_count_rejections": work_rejections,
        "functional_failures": counts["FUNCTIONAL"],
        "integral_float_encoding_slots": sum(
            has_integral_float(row.get("program", {})) for row in generated
        ),
        "ready": fraction >= threshold["model_valid_fraction_min"]
        and work_rejections <= threshold["work_count_rejections_max"]
        and counts["FUNCTIONAL"] <= threshold["functional_failures_max"],
        "thresholds": threshold,
    }


def archive(root, destination):
    previous = Path("results/ibex_temporal_development_v1")
    manifest = json.loads((destination / "manifest.json").read_text())
    (destination / "witnesses").mkdir(parents=True, exist_ok=True)
    for name in manifest["targets"]:
        shutil.copy2(previous / "witnesses" / f"{name}.json", destination / "witnesses")
        shutil.copytree(
            previous / "gate-evidence" / name,
            destination / "gate-evidence" / name,
            dirs_exist_ok=True,
        )
        for seed in manifest["seeds"]:
            relative = Path("panel") / name / f"seed-{seed}" / "random/trials.jsonl"
            target = destination / "v1_random" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(previous / relative, target)
    shutil.copy2(previous / "manifest.json", destination / "v1_manifest.json")
    shutil.copy2(
        previous / "gate-evidence/check_all/profile.json",
        destination / "v1_check_all_profile.json",
    )
    base_archive(root, destination)
    # Preserve failures' diagnostic logs as well as every successful state check.
    for path in sorted((root / "cache").glob("*/driver.log")):
        target = destination / "evaluations" / path.parent.name
        if target.exists():
            shutil.copy2(path, target / path.name)
            for name in ("compile.log", "simulator.log"):
                source = path.parent / "run" / name
                if source.exists():
                    (target / "run").mkdir(exist_ok=True)
                    shutil.copy2(source, target / "run" / name)
    report = readiness(destination)
    (destination / "readiness.json").write_text(json.dumps(report, indent=2) + "\n")
    index = {
        str(p.relative_to(destination)): file_sha256(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file() and p.name != "sha256.json"
    }
    (destination / "sha256.json").write_text(json.dumps(index, indent=2) + "\n")
    return verify(destination)


def verify(destination):
    result = base_verify(destination)
    report = readiness(destination)
    if report != json.loads((destination / "readiness.json").read_text()):
        raise ValueError("readiness arithmetic mismatch")
    from experiments.ibex_temporal_v2.program import from_v1

    matched = 0
    for path in sorted(
        (destination / "v1_random/panel").glob("*/*/random/trials.jsonl")
    ):
        relative = path.relative_to(destination / "v1_random")
        old = [json.loads(line) for line in path.read_text().splitlines()]
        new = [
            json.loads(line)
            for line in (destination / relative).read_text().splitlines()
        ]
        if len(old) != len(new):
            raise ValueError("random replay proposal count differs")
        for a, b in zip(old, new):
            if from_v1(a["program"]) != b["program"] or any(
                a[k] != b[k]
                for k in ("slot", "valid", "stage", "rates", "loss", "best_loss")
            ):
                raise ValueError("v1 random replay differs under v2 embedding")
            matched += 1
    manifest = json.loads((destination / "manifest.json").read_text())
    expected = len(manifest["targets"]) * len(manifest["seeds"]) * manifest["budget"]
    if matched != expected:
        raise ValueError("incomplete random replay evidence")
    return {**result, "readiness": report, "identical_v1_random_slots": matched}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        report = verify(args.archive)
    elif args.root is not None:
        report = archive(args.root, args.archive)
    else:
        parser.error("--root is required for archival")
    print(json.dumps(report, indent=2))
