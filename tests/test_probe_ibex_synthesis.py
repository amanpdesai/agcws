import json
from pathlib import Path

from scripts.probe_ibex_synthesis import main, resolve_source_path


def test_resolve_source_path_remaps_container_root(tmp_path: Path):
    source = tmp_path / "third_party" / "ibex" / "rtl.sv"
    source.parent.mkdir(parents=True)
    source.write_text("module core; endmodule\n")
    assert resolve_source_path("/workspace/third_party/ibex/rtl.sv", tmp_path) == source


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
    assert len(record["sources_sha256"]) == 64
    assert "-Q" not in record["command"]


def test_core_probe_does_not_add_unrelated_memload_include_dirs(tmp_path: Path, monkeypatch):
    source = tmp_path / "core.sv"
    source.write_text("module ibex_core; endmodule\n")
    unrelated = tmp_path / "simple-system" / "prim_util_memload.svh"
    unrelated.parent.mkdir()
    unrelated.write_text("initial begin end\n")
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps({"sources": [{"path": str(source)}]}))
    monkeypatch.setenv("AGCWS_SLANG_PLUGIN", "plugin.so")
    monkeypatch.setenv("AGCWS_YOSYS", "false")
    monkeypatch.setattr("sys.argv", ["probe", str(sources), "--top", "ibex_core",
                                      "--out", str(tmp_path / "out")])
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 1
    record = json.loads((tmp_path / "out" / "manifest.json").read_text())
    assert str(unrelated.parent) not in " ".join(record["command"])
