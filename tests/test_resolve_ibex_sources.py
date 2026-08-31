from pathlib import Path
import pytest

from scripts.resolve_ibex_sources import (add_declared_fileset, find_eda_manifest,
                                          require_toplevel, resolve_manifest)
from scripts.resolve_ibex_sources import add_include_root, add_toplevel_fallback


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


def test_require_toplevel_rejects_incomplete_closure(tmp_path: Path):
    source = tmp_path / "core.sv"
    source.write_text("module other; endmodule\n")
    with pytest.raises(ValueError, match="does not contain top-level module core"):
        require_toplevel([{"path": str(source)}], "core")


def test_add_declared_fileset_adds_sv_sources(tmp_path: Path):
    source = tmp_path / "rtl" / "core.sv"
    source.parent.mkdir()
    source.write_text("module core; endmodule\n")
    core = tmp_path / "core.core"
    core.write_text("filesets:\n  files_rtl:\n    files:\n      - rtl/core.sv\n")
    sources, includes = [], []
    add_declared_fileset(core, "files_rtl", sources, includes)
    assert sources[0]["path"] == str(source.resolve())
    assert includes == [str(source.parent.resolve())]


def test_add_toplevel_fallback_adds_checked_out_top(tmp_path: Path):
    top = tmp_path / "rtl" / "ibex_top.sv"
    top.parent.mkdir()
    top.write_text("module ibex_top; endmodule\n")
    sources, includes = [], []
    add_toplevel_fallback(tmp_path, "ibex_top", sources, includes)
    assert sources[0]["path"] == str(top.resolve())
    assert includes == [str(top.parent.resolve())]


def test_add_include_root_records_existing_include_only_directory(tmp_path: Path):
    include_dir = tmp_path / "include"
    include_dir.mkdir()
    includes = []
    add_include_root(include_dir, includes)
    assert includes == [str(include_dir.resolve())]


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
