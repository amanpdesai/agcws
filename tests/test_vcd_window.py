import pytest

from analysis.vcd_window import window


def test_own_timescale_and_span(tmp_path):
    source = tmp_path / 'wave.vcd'
    source.write_text('$timescale\n10 ps\n$end\n$enddefinitions $end\n#0\n0!\n#200\n1!\n')
    result = window(source)
    assert result['duration_s'] == pytest.approx(2e-9)
    assert result['last_timestamp'] == 200


def test_large_final_event_does_not_require_entire_waveform_in_memory(tmp_path):
    source = tmp_path / 'wave.vcd'
    source.write_text('$timescale 1 ns $end\n#0\n#100\n' + '0!\n' * 50000)
    assert window(source)['duration_s'] == pytest.approx(1e-7)


def test_missing_timescale_fails(tmp_path):
    source = tmp_path / 'wave.vcd'
    source.write_text('#0\n#100\n')
    with pytest.raises(ValueError):
        window(source)
