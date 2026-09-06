import pytest

from validation.window_grid import grid


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
