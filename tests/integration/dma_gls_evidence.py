"""CPU-only DMA diagnostic; never promotes changed frozen sources to a match.

Run from the repository root with the project Python environment.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from agcws.core import config
from agcws.designs.aes.gls import sha
from agcws.designs.dma.backend import DmaTemporal
from agcws.studies.finalists import select, verify


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    root = Path("out/strong-continuation-v1/dma")
    out = Path("out/dma-gls-integration-v1").resolve()
    out.mkdir(exist_ok=True)
    plan = select([root], allow_partial=True)
    verify(plan)
    case = plan["cases"][0]
    manifest = json.loads((root / "manifest.json").read_text())
    changed = [p for p, h in manifest["sources"].items()
               if not Path(p).is_file() or sha(Path(p)) != h]
    write(out / "selection.json", plan)
    write(out / "source-audit.json", {
        "frozen_source_match": not changed, "changed_or_missing": changed,
        "case": case, "plan_sha256": plan["sha256"],
        "claim": "Diagnostic replay only when frozen_source_match is false."})
    rtl = out / "rtl"
    rtl.mkdir(exist_ok=False)
    lowered = DmaTemporal().adapter().elaborate(case["program"])
    write(rtl / "workload.json", lowered["workload"])
    env = dict(os.environ, AGCWS_DMA_TEST_MODULE="axi_dma_pipelined_tb",
               AGCWS_DMA_OBSERVATION_CYCLES="9216", AGCWS_BIT_ACTIVITY_CYCLES="9216",
               AGCWS_DMA_TRAILING_IDLE=str(lowered["trailing_idle_cycles"]),
               AGCWS_ACTIVITY_SCOPE="axi_dma", AGCWS_PYTHON=sys.executable,
               AGCWS_FST2VCD=str(config.FST2VCD))
    command = [sys.executable, "-m", "agcws.designs.dma.simulate",
               str(rtl / "workload.json"), str(rtl)]
    with (rtl / "driver.log").open("w") as log:
        subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    activity = json.loads((rtl / "activity.json").read_text())
    samples = activity["per_cycle_toggles"]
    rates = [sum(samples[i*1152:(i+1)*1152])/1152 for i in range(8)]
    write(out / "rtl-match.json", {
        "exact_rates_match": rates == case["rates"], "actual": rates,
        "frozen": case["rates"], "activity_sha256": sha(rtl / "activity.json"),
        "command": command, "frozen_source_match": not changed})
    print(json.dumps({"rates_match": rates == case["rates"], "source_match": not changed}))


if __name__ == "__main__":
    main()
