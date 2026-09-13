import runpy
from pathlib import Path

import pytest

from agcws.nodes.activity import parse_vcd

functions = runpy.run_path("scripts/prepare_redmule_timed.py")
ROOT = Path("third_party/redmule/target/sim/src")


def test_derived_harness_preserves_license_and_completion_gate():
    original = (ROOT / "redmule_tb.sv").read_text()
    timed = functions["timed_testbench"](original)
    assert timed.startswith(original.split("timeunit")[0])
    assert timed.count("$finish;") == 1
    assert "repeat (observation_cycles) @(posedge clk_i);" in timed
    assert "if (!reference_done) $fatal" in timed
    assert "reference_done = 1;" in timed
    assert "32'h80000008" in timed and "timer_read_data" in timed
    assert "REDMULE_INCOMPLETE" in timed
    assert "$error(\"[TB] - errors=%08x\", errors);" in timed


def test_derivation_refuses_missing_or_ambiguous_anchor():
    replace = functions["replace_once"]
    for text in ("missing", "anchor anchor"):
        with pytest.raises(ValueError, match="upstream harness changed"):
            replace(text, "anchor", "replacement")


def test_wrapper_clock_is_continuous_and_waveform_enabled():
    timed = functions["timed_wrapper"]((ROOT / "redmule_tb_wrap.sv").read_text())
    assert "SPDX-License-Identifier: SHL-0.51" in timed
    assert "forever #(TCP/2) clk = ~clk;" in timed
    assert '$dumpfile("activity.fst")' in timed
    assert "while(1) cycle();" not in timed


def test_qualified_clock_excludes_other_clocks_with_same_leaf_name(tmp_path):
    vcd = tmp_path / "clocks.vcd"
    vcd.write_text("""$scope module top $end
$var wire 1 ! clk $end
$scope module gated $end
$var wire 1 # clk $end
$upscope $end
$upscope $end
$enddefinitions $end
#0
0!
0#
#5
1!
1#
#10
0!
0#
#15
1!
#20
0!
""")
    assert parse_vcd(vcd, "top.clk", 2)["clock_edges"] == 2
    assert parse_vcd(vcd, "top.gated.clk", 2)["clock_edges"] == 1
