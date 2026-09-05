from pathlib import Path

from agcws.nodes.coverage import read_line_coverage
from agcws.nodes.activity import parse_vcd


def test_coverage_excludes_testbench_and_preserves_unhit_points(tmp_path):
    path = tmp_path / 'coverage.dat'
    path.write_text("C '\x01f\x02rtl.sv\x01l\x021\x01t\x02line\x01h\x02tb.dut' 7\n"
                    "C '\x01f\x02rtl.sv\x01l\x022\x01t\x02line\x01h\x02tb.dut' 0\n"
                    "C '\x01f\x02tb.sv\x01l\x021\x01t\x02line\x01h\x02tb' 9\n")
    assert sorted(read_line_coverage(path, Path('.'), 'tb.dut').values()) == [0, 7]


def test_scoped_activity_excludes_harness_and_counts_alias_once(tmp_path):
    path = tmp_path / 'activity.vcd'
    path.write_text('$scope module tb $end\n$var wire 1 ! clk_i $end\n'
                    '$var wire 1 # harness $end\n$scope module dut $end\n'
                    '$var wire 1 $ state $end\n$var wire 1 $ alias $end\n'
                    '$upscope $end\n$upscope $end\n$enddefinitions $end\n'
                    '#0\n0!\n0#\n0$\n#5\n1!\n1#\n1$\n#10\n0!\n0#\n')
    data = parse_vcd(path, scope_prefix='tb.dut')
    assert data['total_transitions'] == 1
    assert data['clock_edges'] == 1
