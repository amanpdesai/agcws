"""Real CPU equivalence check for integral-float encodings and feedback windows."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from agcws.provenance import file_sha256


def gate(root):
    previous = Path("out/ibex-expressiveness-v2/gate/partial")
    original = Path("out/ibex-expressiveness-v2/gate-inputs/partial.json")
    source = root / "numeric-input.json"
    with source.open("x") as output:
        output.write(
            json.dumps(json.loads(original.read_text(), parse_int=float), indent=2)
            + "\n"
        )
    with (root / "gate-driver.log").open("w") as log:
        subprocess.run(
            [
                "bash",
                "docker/run.sh",
                "python3",
                "-m",
                "experiments.ibex_temporal_v3.evaluate",
                "--program",
                "out/numeric-input.json",
                "--out",
                "out/numeric-gate",
            ],
            env={
                **os.environ,
                "AGCWS_CONTAINER_IMAGE": "agcws:window-validation-v1",
                "AGCWS_CONTAINER_OUTPUT": str(root.resolve()),
            },
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    current = root / "numeric-gate"
    old = json.loads((previous / "profile.json").read_text())
    new = json.loads((current / "profile.json").read_text())
    for field in (
        "window_bit_transitions",
        "clock_edges",
        "begin_tick",
        "end_tick",
        "markers",
    ):
        if old[field] != new[field]:
            raise ValueError(f"numeric replay changed {field}")
    if file_sha256(previous / "program.S") != file_sha256(current / "program.S"):
        raise ValueError("numeric replay changed assembly")
    for field in ("expected", "marker_pcs"):
        a = json.loads((previous / "functional.json").read_text())[field]
        b = json.loads((current / "functional.json").read_text())[field]
        if a != b:
            raise ValueError(f"numeric replay changed architectural contract: {field}")
    feedback = json.loads((current / "feedback.json").read_text())
    if any(feedback[k] != new[k] for k in ("begin_tick", "end_tick")):
        raise ValueError("feedback/activity window mismatch")
    result = {
        "numeric_equivalence": True,
        "same_activity_window": True,
        "input_sha256": file_sha256(source),
        "feedback_sha256": file_sha256(current / "feedback.json"),
        "profile_sha256": file_sha256(current / "profile.json"),
    }
    (root / "gate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    gate(parser.parse_args().root)
