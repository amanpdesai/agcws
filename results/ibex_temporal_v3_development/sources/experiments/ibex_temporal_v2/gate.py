"""Architectural and cross-version measurement gate, before model calls."""

import argparse
import concurrent.futures
import json
import os
import subprocess
from itertools import cycle, islice
from pathlib import Path

from experiments.ibex_temporal_v1.witnesses import witness
from experiments.ibex_temporal_v2.program import from_v1


def cases():
    operations = [
        {"op": op, "dst": 2 + (i % 6), "a": i % 8, "b": (i + 1) % 8}
        for i, op in enumerate(
            ("add", "xor", "and", "or", "sll", "srl", "mul", "divu", "cmovz")
        )
    ]
    operations += [{"op": "load", "dst": 3, "a": 1}, {"op": "store", "a": 1, "b": 2}]
    base = {"registers": [0, 17, 0xFFFFFFFF, 3, 4, 5, 6, 7], "memory_seed": 123}
    return {
        "embedded": from_v1(witness("check_all")),
        "partial": {
            **base,
            "segments": [
                {
                    "weight": i + 1,
                    "release": 0,
                    "body": list(
                        islice(cycle(operations[i:] + operations[:i]), length)
                    ),
                }
                for i, length in enumerate([3, 5, 6, 7, 8, 3, 5, 7])
            ],
        },
        "tiny": {
            **base,
            "segments": [
                {
                    "weight": 4096 if i == 0 else 1,
                    "release": 0,
                    "body": list(islice(cycle(operations[i:] + operations[:i]), 8)),
                }
                for i in range(8)
            ],
        },
    }


def gate(root):
    inputs = root / "gate-inputs"
    inputs.mkdir(parents=True, exist_ok=False)
    for name, program in cases().items():
        (inputs / f"{name}.json").write_text(json.dumps(program, indent=2) + "\n")
    environment = {
        **os.environ,
        "AGCWS_CONTAINER_IMAGE": "agcws:window-validation-v1",
        "AGCWS_CONTAINER_OUTPUT": str(root.resolve()),
    }

    def one(name):
        with (root / f"{name}.log").open("w") as log:
            subprocess.run(
                [
                    "bash",
                    "docker/run.sh",
                    "python3",
                    "-m",
                    "experiments.ibex_temporal_v2.evaluate",
                    "--program",
                    f"out/gate-inputs/{name}.json",
                    "--out",
                    f"out/gate/{name}",
                ],
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        result = json.loads((root / "gate" / name / "profile.json").read_text())
        print(name, "passed", flush=True)
        return name, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = dict(pool.map(one, cases()))
    old = json.loads(
        Path("results/ibex_temporal_development_v1/gate.json").read_text()
    )["check_all"]
    assert (
        results["embedded"]["window_bit_transitions"] == old["window_bit_transitions"]
    )
    assert results["embedded"]["markers"] == old["markers"]
    (root / "gate.json").write_text(json.dumps(results, indent=2) + "\n")
    print("V2_GATE_PASSED", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    gate(parser.parse_args().root)
