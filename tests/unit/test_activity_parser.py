from pathlib import Path

import pytest

from agcws.evaluation.activity.generic import attribute_regions, extract_activity, normalize_windows
from agcws.evaluation.activity.parse import parse


def test_extract_activity_requires_waveform(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="did not produce waveform"):
        extract_activity(["true"], tmp_path / "missing.vcd", tmp_path / "activity")


def test_extract_activity_requires_saif(tmp_path: Path):
    waveform = tmp_path / "activity.vcd"
    waveform.write_text("$enddefinitions $end\n#0\n")
    with pytest.raises(FileNotFoundError, match="did not produce SAIF"):
        extract_activity(["true"], waveform, tmp_path / "activity")


def test_extract_activity_rejects_failed_command(tmp_path: Path):
    waveform = tmp_path / "activity.vcd"
    waveform.write_text("$enddefinitions $end\n")
    with pytest.raises(RuntimeError, match="activity command failed"):
        extract_activity(["false"], waveform, tmp_path / "activity")

def test_parse_smoke_vcd(tmp_path):
    waveform = tmp_path / "activity.vcd"
    lines = ["$scope module dut $end", "$var wire 1 ! clk_i $end",
             "$var wire 1 # data $end", "$upscope $end", "$enddefinitions $end",
             "#0", "0!", "0#"]
    for cycle in range(16):
        lines.extend([f"#{cycle*10+5}", "1!", f"{(cycle+1)%2}#",
                      f"#{cycle*10+10}", "0!"])
    waveform.write_text("\n".join(lines) + "\n")
    result = parse(waveform, windows=8)
    assert result["clock_edges"] == 16
    assert result["total_transitions"] == 48
    assert result["per_cycle_toggles"] == [3] * 16
    assert result["window_toggles"] == [6] * 8
    assert len(result["window_toggles"]) == 8
    assert len(result["per_cycle_toggles"]) == result["clock_edges"]
    assert sum(result["per_cycle_toggles"]) == result["total_transitions"]
    assert len(result["waveform_sha256"]) == 64


def test_region_attribution_keeps_unmatched_and_ambiguous_signals_visible():
    result = attribute_regions(
        {"ctrl_ready": 3, "data_bus": 5, "ctrl_data": 7, "other": 2},
        {"control": ("ctrl_",), "data": ("data_",)},
    )
    assert result == {"control": 10.0, "data": 5.0, "unattributed": 2.0}


def test_normalize_windows_handles_peak_and_zero_profiles():
    assert normalize_windows([2, 4, 1]) == (0.5, 1.0, 0.25)
    assert normalize_windows([0, 0]) == (0.0, 0.0)
