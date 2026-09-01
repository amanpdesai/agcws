import json
from pathlib import Path

from scripts.write_ibex_result import main


def test_ibex_result_records_portable_inputs(tmp_path: Path, monkeypatch):
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    (artifact / "workload.json").write_text('{"program": []}\n')
    (artifact / "sim.fst").write_bytes(b"fst")
    (artifact / "ibex_simple_system_pcount.csv").write_text("Cycles,10010\nInstructions Retired,10000\n")
    monkeypatch.setattr("sys.argv", ["write_ibex_result", str(artifact), "unused.json"])
    main()
    result = json.loads((artifact / "result.json").read_text())
    assert result["valid"]
    assert result["useful_work"] == 10000
    assert result["useful_work_floor"] == 10000
    assert set(result["provenance"]["inputs"]) == {"workload", "waveform", "performance_counters"}


def test_ibex_result_uses_environment_tool_paths(tmp_path: Path, monkeypatch):
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    (artifact / "workload.json").write_text('{"program": []}\n')
    (artifact / "sim.fst").write_bytes(b"fst")
    (artifact / "ibex_simple_system_pcount.csv").write_text(
        "Instructions Retired,10000\n"
    )
    monkeypatch.setenv("AGCWS_VERILATOR", "/custom/verilator")
    monkeypatch.setenv("AGCWS_RISCV_GCC", "/custom/riscv-gcc")
    monkeypatch.setattr("sys.argv", ["write_ibex_result", str(artifact), "unused.json"])
    main()
    # Missing custom tools are represented as unavailable versions, but the
    # command paths are exercised through the environment contract.
    result = json.loads((artifact / "result.json").read_text())
    assert result["provenance"]["tools"]["verilator"] is None
    assert result["provenance"]["tools"]["riscv_gcc"] is None
