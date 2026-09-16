"""Run one frozen CPU panel with a free-disk guard, not an execution timeout."""

import argparse
import os
import shutil
import signal
import subprocess
import sys

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.storage import read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", choices=("aes", "dma", "ibex", "mesh", "redmule"))
    parser.add_argument("--panel", choices=("baselines-model-v1", "baselines-model-v1-dev"),
                        default="baselines-model-v1")
    args = parser.parse_args()
    for command in ("zstd", "fst2vcd", "find"):
        if shutil.which(command) is None:
            raise RuntimeError(f"waveform retention requires host executable: {command}")
    root = ROOT / "out" / args.panel / args.design
    manifest = verify_inputs(ROOT, root)
    if manifest["models"] or manifest["spec"]["policies"] != ["phase-random", "phase-ga", "phase-model"]:
        raise ValueError("baseline runner prohibits model arms")
    reserve = 500*1024**3
    if shutil.disk_usage(ROOT).free < reserve:
        raise RuntimeError("disk reserve too low to start")
    with (root / "runner.log").open("a", buffering=1) as log:
        process = subprocess.Popen([sys.executable, "-u", "-m", "agcws.pipeline", "run",
                                   "--directory", str(root), "--execute"], cwd=ROOT,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                   env={**os.environ, "OPENBLAS_NUM_THREADS": "1"})
        print(f"Running {args.design}; PID {process.pid}; log {root / 'runner.log'}", flush=True)
        while True:
            try:
                code = process.wait(timeout=60)
                break
            except subprocess.TimeoutExpired:
                if shutil.disk_usage(ROOT).free < reserve:
                    os.killpg(process.pid, signal.SIGTERM)
                    code = process.wait()
                    log.write("AGCWS_DISK_GUARD_STOP: checkpoints preserved; no automatic restart\n")
                    break
        log.write(f"AGCWS_BASELINE_EXIT_CODE={code}\n")
    if code == 0:
        result = read(root / "complete.json")
        print(f"Completed {result['cells']} cells / {result['slots']} slots", flush=True)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
