import json
from pathlib import Path

from flows.chia_nodes import activity_node


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
