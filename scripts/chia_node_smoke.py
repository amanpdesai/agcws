#!/usr/bin/env python3
"""Run the minimal remote CHIA simulation-to-activity acceptance test."""
from __future__ import annotations

import base64
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ray

from flows.chia_nodes import activity_node, power_node, simulate_node


VCD = """$timescale 1ns $end
$scope module top $end
$var wire 1 ! clk_i $end
$var wire 1 \" data $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
0!
0\"
$end
#5
1!
1\"
#10
0!
0\"
#15
1!
1\"
"""


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="agcws-chia-smoke-") as temp:
        root = Path(temp)
        encoded = base64.b64encode(VCD.encode()).decode()
        command = ["bash", "-lc", f"echo {encoded} | base64 -d > activity.vcd"]
        ray.init(include_dashboard=False, num_cpus=1, ignore_reinit_error=True,
                 logging_level="ERROR")
        try:
            simulation = ray.get(simulate_node.chia_remote(command, str(root)))
            activity = ray.get(activity_node.chia_remote(
                simulation["waveform"], str(root / "activity.json"), windows=2))
            (root / "mapped.v").write_text("module top; endmodule\n")
            (root / "cells.lib").write_text("library(test) {}\n")
            (root / "manifest.json").write_text("{}\n")
            (root / "activity.saif").write_text("(SAIFILE)\n")
            power = ray.get(power_node.chia_remote(
                ["bash", "-lc", "printf 'Total Power = 1.25e-03\\n' > power.rpt"],
                str(root / "mapped.v"), str(root / "cells.lib"),
                str(root / "manifest.json"), str(root / "activity.saif"),
                str(root / "power"),
            ))
        finally:
            ray.shutdown()
    if activity["clock_edges"] != 2 or activity["total_transitions"] != 6:
        raise RuntimeError(f"unexpected CHIA activity result: {activity}")
    if power["mean_power"] != 0.00125 or power["fidelity"] != "synthesis":
        raise RuntimeError(f"unexpected CHIA power result: {power}")
    print("AGCWS_CHIA_NODES_SMOKE_OK")


if __name__ == "__main__":
    main()
