"""Stage hashed inputs for two existing finalists, without host executables."""

import argparse
import json
import shutil
from pathlib import Path

from maintenance.trace_store import digest


def stage(out):
    selection_path = Path("results/structural_temporal_finalists_v1.json")
    selected = json.loads(selection_path.read_text())["cases"]
    archive = Path("results/windowed_power_v1")
    validation = json.loads((archive / "validation.json").read_text())
    if digest(selection_path) != validation["selection_sha256"]:
        raise ValueError("changed selection")
    out.mkdir(parents=True, exist_ok=False)
    cases = []
    for design, synthesis in [
        ("aes", "aes-unmasked-matched-synthesis-v2"),
        ("dma", "axi-dma-synthesis-gls3"),
    ]:
        case = next(
            c
            for c in selected
            if c["design"] == design
            and c["target"] == "random_300"
            and c["policy"] == "random"
        )
        rtl = (
            Path("out/structural-temporal-heldout-v1")
            / case["run"]
            / "evaluations"
            / f"trial-{case['evaluation_index']:05d}"
        )
        if (
            digest(rtl / "activity.json")
            != case["activity_profile"]["provenance"]["activity_sha256"]
        ):
            raise ValueError("changed RTL measurement")
        names = ["workload.json", "activity.json", "activity.vcd"]
        names += (
            ["program.txt", "run.log"]
            if design == "aes"
            else ["sim_build/observed.json", "driver.log"]
        )
        for name in names:
            destination = out / design / "rtl" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rtl / name, destination)
        for name in ["mapped.v", "manifest.json"]:
            destination = out / design / "synthesis" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path("out") / synthesis / name, destination)
        expected = archive / "finalists" / case["replay_id"] / "power.json"
        if (
            digest(expected)
            != validation["artifact_sha256"][str(expected.relative_to(archive))]
        ):
            raise ValueError("changed expected power")
        shutil.copy2(expected, out / design / "expected_power.json")
        cases.append(
            {
                k: case[k]
                for k in [
                    "design",
                    "replay_id",
                    "run",
                    "evaluation_index",
                    "seed",
                    "target",
                    "policy",
                ]
            }
        )
    files = {
        str(p.relative_to(out)): digest(p)
        for p in sorted(out.rglob("*"))
        if p.is_file()
    }
    record = {
        "scope": "Two predeclared existing finalists; container replay, not new research runs.",
        "selection_sha256": digest(selection_path),
        "cases": cases,
        "files": files,
        "power_relative_tolerance": 1e-5,
        "power_absolute_tolerance_w": 1e-12,
    }
    (out / "inputs.json").write_text(json.dumps(record, indent=2) + "\n")
    print("CONTAINER_INPUTS_STAGED", out, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    stage(args.out)
