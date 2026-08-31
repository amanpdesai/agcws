from pathlib import Path
import pytest

from scripts.resolve_ibex_sources import find_eda_manifest, resolve_manifest


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


def test_resolve_manifest_fails_on_missing_source(tmp_path: Path):
    manifest = tmp_path / "manifest.yml"
    manifest.write_text(
        "files:\n"
        "  - file_type: systemVerilogSource\n"
        "    name: missing/core.sv\n"
    )
    with pytest.raises(FileNotFoundError, match="FuseSoC source is missing"):
        resolve_manifest(manifest)


def test_find_eda_manifest_selects_core_manifest(tmp_path: Path):
    expected = tmp_path / "lowrisc_ibex_ibex_top_0.1" / "lint-verilator"
    expected.mkdir(parents=True)
    manifest = expected / "ibex_top_0.1.eda.yml"
    manifest.write_text("files: []\n")
    assert find_eda_manifest(tmp_path, "lowrisc:ibex:ibex_top") == manifest


def test_find_eda_manifest_prefers_lint_when_simulation_manifest_exists(tmp_path: Path):
    lint = tmp_path / "lint-verilator" / "ibex_top_0.1.eda.yml"
    sim = tmp_path / "sim-verilator" / "ibex_top_0.1.eda.yml"
    lint.parent.mkdir()
    sim.parent.mkdir()
    lint.write_text("files: []\n")
    sim.write_text("files: []\n")

    assert find_eda_manifest(tmp_path, "lowrisc:ibex:ibex_top") == lint
