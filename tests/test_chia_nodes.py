import json
from pathlib import Path

from flows.chia_nodes import activity_node, power_node


def test_activity_node_writes_cycle_and_window_artifact(tmp_path: Path):
    waveform = tmp_path / "activity.vcd"
    waveform.write_text(
        "$timescale 1ns $end\n"
        "$scope module top $end\n"
        "$var wire 1 ! clk_i $end\n"
        "$var wire 1 \" data $end\n"
        "$upscope $end\n"
        "$enddefinitions $end\n"
        "#0\n$dumpvars\n0!\n0\"\n$end\n"
        "#5\n1!\n1\"\n#10\n0!\n0\"\n#15\n1!\n1\"\n"
    )
    output = tmp_path / "activity.json"

    result = activity_node(str(waveform), str(output), windows=2)

    activity = json.loads(output.read_text())
    assert result == {"activity": str(output), "clock_edges": 2,
                      "total_transitions": 6}
    assert len(activity["per_cycle_toggles"]) == 2
    assert len(activity["window_toggles"]) == 2


def test_power_node_returns_strict_profile(tmp_path: Path):
    (tmp_path / "mapped.v").write_text("module top; endmodule\n")
    (tmp_path / "cells.lib").write_text("library(test) {}\n")
    (tmp_path / "manifest.json").write_text("{}\n")
    (tmp_path / "activity.saif").write_text("(SAIFILE)\n")
    output = tmp_path / "power"
    result = power_node(
        ["bash", "-lc", "printf 'Total Power = 1.25e-03\\n' > power.rpt"],
        str(tmp_path / "mapped.v"), str(tmp_path / "cells.lib"),
        str(tmp_path / "manifest.json"), str(tmp_path / "activity.saif"),
        str(output),
    )
    assert result["valid"]
    assert result["fidelity"] == "synthesis"
    assert result["mean_power"] == 0.00125
