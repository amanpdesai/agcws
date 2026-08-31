import json
from pathlib import Path

from scripts.probe_ibex_synthesis import main


def test_probe_writes_failure_manifest(tmp_path: Path, monkeypatch):
    source = tmp_path / "core.sv"
    source.write_text("module core; endmodule\n")
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps({"sources": [{"path": str(source)}]}))
    monkeypatch.setenv("AGCWS_SLANG_PLUGIN", "plugin.so")
    monkeypatch.setenv("AGCWS_YOSYS", "false")
    monkeypatch.setattr("sys.argv", ["probe", str(sources), "--out", str(tmp_path / "out")])
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 1
    record = json.loads((tmp_path / "out" / "manifest.json").read_text())
    assert record["returncode"] == 1
    assert record["source_count"] == 1
