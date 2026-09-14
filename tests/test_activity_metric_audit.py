"""Characterize frozen behavior, not endorsements of the measurement contract."""

import runpy

import pytest

from agcws.nodes.activity import parse_vcd


def waveform(tmp_path, declarations, initial, changed):
    path = tmp_path / "probe.vcd"
    path.write_text(
        "$timescale 1 ns $end\n$scope module top $end\n"
        "$var wire 1 ! clk $end\n$scope module dut $end\n"
        + declarations
        + "$upscope $end\n$upscope $end\n$enddefinitions $end\n"
        + "#0\n0!\n" + initial + "#5\n1!\n#6\n" + changed
        + "#10\n0!\n#15\n1!\n"
    )
    return parse_vcd(path, "top.clk", 2, "top.dut")


def test_equivalent_bus_and_scalar_representation_changes_event_count(tmp_path):
    bus = waveform(tmp_path, "$var wire 32 bus data $end\n",
                   "b0 bus\n", "b" + "1" * 32 + " bus\n")
    scalars = waveform(
        tmp_path,
        "".join(f"$var wire 1 s{i} data_{i} $end\n" for i in range(32)),
        "".join(f"0s{i}\n" for i in range(32)),
        "".join(f"1s{i}\n" for i in range(32)),
    )
    assert bus["clock_edges"] == scalars["clock_edges"] == 2
    assert bus["total_transitions"] == 1
    assert scalars["total_transitions"] == 32


def test_vector_zero_padding_counts_as_an_event(tmp_path):
    result = waveform(tmp_path, "$var wire 32 bus data $end\n",
                      "b0 bus\n", "b00 bus\n")
    assert result["total_transitions"] == 1


def test_unknown_value_change_is_counted_not_rejected(tmp_path):
    result = waveform(tmp_path, "$var wire 1 s data $end\n", "0s\n", "xs\n")
    assert result["total_transitions"] == 1


def test_independent_recount_counts_bits_padding_and_unknown_separately(tmp_path):
    path = tmp_path / "bits.vcd"
    path.write_text(
        "$scope module top $end\n$var wire 1 ! clk $end\n"
        "$scope module dut $end\n$var wire 8 b data $end\n"
        "$upscope $end\n$upscope $end\n$enddefinitions $end\n"
        "#0\n0!\nb0 b\n#1\n1!\nb11111111 b\n"
        "#2\n0!\nb011111111 b\n"
        + "".join(f"#{2*i+1}\n1!\n#{2*i+2}\n0!\n" for i in range(1, 8))
    )
    recount = runpy.run_path("analysis/activity_recount.py")["recount"]
    with pytest.raises(ValueError, match="width"):
        recount(path, "top.dut", "top.clk")
    path.write_text(path.read_text().replace("b011111111 b", "b0 b\n"))
    result = recount(path, "top.dut", "top.clk")
    assert result["bin_counts"][0] == [2, 16, 0]
    assert result["clock_edges"] == 8
    assert not result["clock_in_activity_scope"]
    path.write_text(path.read_text().replace("b11111111 b", "bx b"))
    result = recount(path, "top.dut", "top.clk")
    assert result["bin_counts"][0] == [2, 0, 2]
