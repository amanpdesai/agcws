import pytest

from agcws.nodes.bit_activity import Observation, binary_state, stream_bits


def trace(events, declarations="$var wire 8 d data $end\n"):
    header = ("$timescale 1 ns $end\n$scope module top $end\n"
              "$var wire 1 c clk $end\n$scope module dut $end\n"
              + declarations + "$upscope $end\n$upscope $end\n$enddefinitions $end\n")
    lines = [header, "#0\n0c\n"]
    for tick in range(1, 17):
        lines.append(f"#{tick}\n")
        lines.extend(events.get(tick, []))
        lines.append("1c\n" if tick % 2 else "0c\n")
    return "".join(lines).splitlines()


SPEC = Observation("top.dut", "top.clk", 8)


def test_width_normalization_and_bit_mask():
    assert binary_state("0", 8) == binary_state("000", 8) == (0, 255)
    assert binary_state("x", 8) == (0, 0)
    assert binary_state("1x", 2) == (2, 2)
    with pytest.raises(ValueError):
        binary_state("111", 2)


def test_timestamp_grouping_excludes_clock_and_preserves_bit_counts():
    events = {1: ["b0 d\n"], 3: ["b00 d\n"], 5: ["b111 d\n"]}
    result = stream_bits(trace(events), SPEC)
    assert result["window_bit_transitions"] == [0, 0, 3, 0, 0, 0, 0, 0]
    assert result["selected_bits"] == 8
    assert result["remaining_unknown_bits"] == 0
    text = "\n".join(trace(events)).replace("b111 d\n1c", "1c\nb111 d")
    assert stream_bits(text.splitlines(), SPEC) == result


def test_bus_and_scalar_forms_have_identical_activity():
    bus = stream_bits(trace({1: ["b0 d\n"], 5: ["b11111111 d\n"]}), SPEC)
    declarations = "".join(f"$var wire 1 d{i} data_{i} $end\n" for i in range(8))
    scalar = stream_bits(trace({1: [f"0d{i}\n" for i in range(8)],
                                5: [f"1d{i}\n" for i in range(8)]}, declarations), SPEC)
    assert scalar["window_bit_transitions"] == bus["window_bit_transitions"]
    assert sum(scalar["window_bit_transitions"]) == 8


def test_unknown_initialization_is_recorded_but_regression_rejected():
    result = stream_bits(trace({1: ["bx d\n"], 3: ["b0 d\n"], 5: ["b1 d\n"]}), SPEC)
    assert sum(result["window_bit_transitions"]) == 1
    with pytest.raises(ValueError, match="became unknown"):
        stream_bits(trace({1: ["b0 d\n"], 5: ["bx d\n"]}), SPEC)


def test_missing_clock_and_short_observation_fail_closed():
    with pytest.raises(ValueError, match="clock"):
        stream_bits(trace({}), Observation("top.dut", "top.missing", 8))
    with pytest.raises(ValueError, match="observation"):
        stream_bits(trace({}), Observation("top.dut", "top.clk", 9))


def test_half_open_marker_boundary_and_known_carried_state():
    spec = Observation("top.dut", "top.clk", 4, windows=2,
                       begin=5, end=13, period=2, require_known_initial=True)
    result = stream_bits(trace({1: ["b0 d\n"], 5: ["b1 d\n"], 13: ["b0 d\n"]}), spec)
    assert result["window_bit_transitions"] == [1, 0]
    with pytest.raises(ValueError, match="carried state"):
        stream_bits(trace({5: ["b0 d\n"]}), spec)


def test_marker_between_edges_keeps_first_event_and_half_open_bin_ownership():
    spec = Observation("top.dut", "top.clk", 4, windows=2,
                       begin=4, end=12, period=2, require_known_initial=True)
    result = stream_bits(trace({1: ["b0 d\n"], 4: ["b1 d\n"],
                                8: ["b0 d\n"], 12: ["b1 d\n"]}), spec)
    assert result["window_bit_transitions"] == [1, 1]
