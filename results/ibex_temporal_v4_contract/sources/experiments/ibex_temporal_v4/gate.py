"""Real-CPU check that diagnostic labels preserve loadable bytes and activity."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v4.evaluate import write


def gate(root, source):
    root = root.resolve()
    gate_root = root / "equivalence"
    gate_root.mkdir(exist_ok=False)
    write(gate_root / "input.json", json.loads(source.read_text()))
    environment = {
        **os.environ,
        "AGCWS_CONTAINER_IMAGE": "agcws:window-validation-v1",
        "AGCWS_CONTAINER_OUTPUT": str(root),
    }
    image = subprocess.check_output(
        [
            "docker",
            "image",
            "inspect",
            environment["AGCWS_CONTAINER_IMAGE"],
            "--format",
            "{{.Id}}",
        ],
        text=True,
    ).strip()
    for kind in ("original", "annotated"):
        command = [
            "bash",
            "docker/run.sh",
            "python3",
            "-m",
            "experiments.ibex_temporal_v4.evaluate",
            "--program",
            "out/equivalence/input.json",
            "--out",
            f"out/equivalence/{kind}",
        ]
        if kind == "original":
            command.append("--original")
        with (gate_root / f"{kind}.log").open("w") as log:
            subprocess.run(
                command,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
    a, b = gate_root / "original", gate_root / "annotated"
    if file_sha256(a / "loadable.bin") != file_sha256(b / "loadable.bin"):
        raise ValueError("diagnostic labels changed loadable program bytes")
    for filename, fields in (
        (
            "profile.json",
            (
                "window_bit_transitions",
                "clock_edges",
                "begin_tick",
                "end_tick",
                "markers",
            ),
        ),
        ("functional.json", ("expected", "marker_pcs")),
        (
            "feedback.json",
            ("retired_classes", "retired_per_bin", "body_completion_cycles"),
        ),
    ):
        left, right = [json.loads((p / filename).read_text()) for p in (a, b)]
        if any(left[k] != right[k] for k in fields):
            raise ValueError(f"diagnostic equivalence failed: {filename}")
    result = {
        "loadable_bytes_identical": True,
        "architectural_state_identical": True,
        "activity_identical": True,
        "image_id": image,
        "evidence": {
            str(p.relative_to(gate_root)): file_sha256(p)
            for p in sorted(gate_root.rglob("*"))
            if p.is_file() and p.suffix in (".json", ".S", ".bin")
        },
    }
    write(gate_root / "gate.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    gate(args.root, args.source)
