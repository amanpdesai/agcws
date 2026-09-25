import pytest

from agcws.evaluation.power.windows import aligned_grids
from agcws.evaluation.waveforms.grid import grid


def trace(extra=''):
    header = ('$timescale 1ps $end\n$scope module top $end\n'
              '$var wire 1 ! clk $end\n$var wire 1 " A $end\n'
              '$upscope $end\n$enddefinitions $end\n#0\n0!\n0"\n')
    return header + ''.join(f'#{t}\n{int(t % 10 == 5)}!\n' + (extra if t == 20 else '')
                            for t in range(5, 161, 5))


def test_clock_partitions_use_empty_boundaries_and_exact_full_duration(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace())
    actual = grid(p, 'clk', 16)
    assert actual['bounds_ticks'] == [0, 24, 44, 64, 84, 104, 124, 144, 160]
    assert actual['edge_indices'] == list(range(0, 17, 2))
    assert sum(actual['durations_ticks']) == 160
    assert actual['span']['timescale_s'] == 1e-12


def test_boundary_collision_is_rejected_not_silently_double_counted(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace('#24\n1"\n'))
    with pytest.raises(ValueError, match='not event-free'):
        grid(p, 'clk', 16)


def test_wrong_clock_count_fails(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace())
    with pytest.raises(ValueError, match='rising-edge count'):
        grid(p, 'clk', 17)


def test_marker_window_excludes_reset_and_tail(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace())
    actual = grid(p, 'top.clk', 8, begin=45, end=125)
    assert actual['bounds_ticks'] == list(range(44, 125, 10))
    assert actual['durations_ticks'] == [10] * 8
    assert actual['clock_edges'] == 8


def test_marker_alignment_allows_only_absolute_offset(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace())
    left = grid(p, 'top.clk', 8, begin=45, end=125)
    right = grid(p, 'top.clk', 8, begin=55, end=135)
    assert aligned_grids(left, right, marker_bounded=True)
    assert not aligned_grids(left, right)
    shifted = grid(p, 'top.clk', 8, begin=47, end=127)
    assert not aligned_grids(left, shifted, marker_bounded=True)
    assert not aligned_grids(left, {**right, 'durations_s': [1] * 8}, marker_bounded=True)


def test_marker_boundary_cannot_double_count_events(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace().replace('#40\n', '#39\n1"\n#40\n'))
    with pytest.raises(ValueError, match='not event-free'):
        grid(p, 'top.clk', 8, begin=40, end=120)


def test_qualified_clock_rejects_wrong_hierarchy(tmp_path):
    p = tmp_path / 'trace.vcd'
    p.write_text(trace())
    with pytest.raises(ValueError, match='ambiguous clock'):
        grid(p, 'other.clk', 16)
