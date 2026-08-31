from pathlib import Path
from scripts.parse_vcd_activity import parse

def test_parse_smoke_vcd():
    result = parse(Path("out/aes-core-smoke/activity.vcd"), windows=8)
    assert result["clock_edges"] > 0
    assert result["total_transitions"] > 0
    assert len(result["window_toggles"]) == 8
