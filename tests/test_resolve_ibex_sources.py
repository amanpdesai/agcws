from pathlib import Path

from scripts.resolve_ibex_sources import resolve_manifest


def test_resolve_manifest_filters_and_hashes_sv(tmp_path: Path):
    source = tmp_path / "src" / "core.sv"
    source.parent.mkdir()
    source.write_text("module core; endmodule\n")
    manifest = tmp_path / "manifest.yml"
    manifest.write_text(
        "files:\n"
        "  - file_type: systemVerilogSource\n"
        "    name: src/core.sv\n"
        "  - file_type: vlt\n"
        "    name: lint.vlt\n"
    )
    result, include_dirs = resolve_manifest(manifest)
    assert len(result) == 1
    assert result[0]["path"] == str(source.resolve())
    assert result[0]["bytes"] == source.stat().st_size
    assert len(result[0]["sha256"]) == 64
    assert include_dirs == [str(source.parent.resolve())]
