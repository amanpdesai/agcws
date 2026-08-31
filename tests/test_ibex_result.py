import json
from pathlib import Path

from scripts.write_ibex_result import main


def test_ibex_result_records_portable_inputs(tmp_path: Path, monkeypatch):
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    (artifact / "workload.json").write_text('{"program": []}\n')
    (artifact / "sim.fst").write_bytes(b"fst")
    (artifact / "ibex_simple_system_pcount.csv").write_text("Cycles,10\nInstructions Retired,12\n")
    monkeypatch.setattr("sys.argv", ["write_ibex_result", str(artifact), "unused.json"])
    main()
    result = json.loads((artifact / "result.json").read_text())
    assert result["valid"]
    assert result["useful_work"] == 12
    assert set(result["provenance"]["inputs"]) == {"workload", "waveform", "performance_counters"}
