from pathlib import Path
import pytest
from scripts.parse_vcd_activity import parse
from agcws.nodes.activity import attribute_regions, extract_activity


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

def test_parse_smoke_vcd():
    result = parse(Path("out/aes-core-smoke/activity.vcd"), windows=8)
    assert result["clock_edges"] > 0
    assert result["total_transitions"] > 0
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
