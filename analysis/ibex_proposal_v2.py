"""Archive the versioned allocation diagnostic without changing the v1 results."""

import argparse
import collections
import json
import shutil
from pathlib import Path

from agcws.provenance import file_sha256
from analysis.ibex_expressiveness import archive as base_archive
from analysis.ibex_expressiveness import verify as base_verify


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
    return {**result, "readiness": report}


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
