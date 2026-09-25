import pytest

from agcws.designs.redmule.bus_trace import triggers


def test_trigger_samples_pre_edge_request_not_post_edge_request(tmp_path):
    path = tmp_path / "bus.vcd"
    path.write_text("""$scope module redmule_tb_wrap $end
$scope module i_redmule_tb $end
$var wire 1 ! clk_i $end
$var wire 1 a data_req $end
$var wire 1 b data_gnt $end
$var wire 1 c data_we $end
$var wire 32 d data_addr $end
$upscope $end
$upscope $end
$enddefinitions $end
#0
0!
0a
1b
1c
b100000000000000000000 d
#5
1!
1a
#10
0!
#15
1!
0a
#20
0!
""")
    result = triggers(path)
    assert result == {"clock_edges": 2, "accepted_trigger_edges": [2]}


def test_missing_harness_signals_fails(tmp_path):
    path = tmp_path / "empty.vcd"
    path.write_text("$enddefinitions $end\n")
    with pytest.raises(ValueError, match="exact timing harness"):
        triggers(path)
