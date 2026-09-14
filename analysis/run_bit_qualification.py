"""Continue a frozen CPU replay through declared qualification without status polling."""

import argparse
import fcntl
import json
import shutil
import subprocess
import sys
from pathlib import Path

from admit_bit_bank import audit
from bit_bank import plan

from agcws.config import ROOT
from agcws.pipeline.storage import ensure, read


def run(root):
    # The replay holds this lock throughout execution; completion wakes us directly.
    with (root / "replay/run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        read(root / "replay/complete.json")
    if not (root / "qualification").exists():
        print(json.dumps(plan(root)), flush=True)
    directory = root / "qualification"
    if (directory / "failure.json").exists():
        return read(directory / "failure.json")
    trace_sizes = [p.stat().st_size for p in (root / "replay/cache").rglob("activity.vcd")]
    trace_sizes += [p.stat().st_size for p in (root / "replay/cache").rglob("sim.fst")]
    largest_trace = max(trace_sizes, default=0)
    if not largest_trace:
        raise ValueError("cannot budget disk without observed waveform sizes")
    for split in ("development", "confirmation"):
        panel = directory / split
        if not panel.exists() or (panel / "complete.json").exists():
            continue
        spec = read(panel / "manifest.json")["spec"]
        slots = len(spec["targets"])*len(spec["policies"])*spec["budget"]
        reserve = int(largest_trace*slots*1.5) + 1024**3
        if shutil.disk_usage(root).free < reserve:
            raise RuntimeError(f"insufficient conservative waveform disk reserve: {reserve} bytes")
        with (directory / f"{split}-runner.log").open("a") as log:
            subprocess.run([sys.executable, "-u", "-m", "agcws.pipeline", "run",
                            "--directory", str(panel), "--execute"],
                           cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    result = audit(root)
    ensure(root / "qualification-complete.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.root.resolve())), flush=True)
