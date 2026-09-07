"""Supervised feasibility jobs; no policy or model comparison."""

import argparse
import concurrent.futures
import json
import os
import subprocess
from pathlib import Path

from experiments.ibex_temporal_v1.witnesses import PATTERNS, witness


def gate(root):
    inputs = root / "gate-inputs"
    inputs.mkdir(parents=True, exist_ok=False)
    for name in PATTERNS:
        (inputs / f"{name}.json").write_text(json.dumps(witness(name), indent=2) + "\n")
    environment = {
        **os.environ,
        "AGCWS_CONTAINER_IMAGE": "agcws:window-validation-v1",
        "AGCWS_CONTAINER_OUTPUT": str(root.resolve()),
    }

    def one(name):
        source = "check_all" if name == "repeat_check" else name
        with (root / f"{name}-gate.log").open("w") as log:
            subprocess.run(
                [
                    "bash",
                    "docker/run.sh",
                    "python3",
                    "-m",
                    "experiments.ibex_temporal_v1.evaluate",
                    "--program",
                    f"out/gate-inputs/{source}.json",
                    "--out",
                    f"out/gate/{name}",
                    "--activity",
                ],
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
        profile = json.loads((root / "gate" / name / "profile.json").read_text())
        print(name, profile["window_rates"], flush=True)
        return name, profile

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows = dict(pool.map(one, [*PATTERNS, "repeat_check"]))
    assert (
        rows["check_all"]["window_bit_transitions"]
        == rows["repeat_check"]["window_bit_transitions"]
    )
    assert rows["check_all"]["markers"] == rows["repeat_check"]["markers"]
    (root / "gate.json").write_text(json.dumps(rows, indent=2) + "\n")
    print("IBEX_GATE_VERIFIED", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    gate(parser.parse_args().root)
