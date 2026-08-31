from pathlib import Path

import pytest

from agcws.nodes.synthesize import synthesize_once


def test_synthesis_cache_requires_netlist(tmp_path: Path):
    liberty = tmp_path / "test.lib"
    liberty.write_text("library(test) {}\n")
    output = tmp_path / "synthesis"
    command = ["sh", "-c", "printf 'module top; endmodule\\n' > mapped.v"]

    first, artifact = synthesize_once(command, output, liberty, "design-a")
    assert first.returncode == 0
    artifact.netlist.unlink()

    second, artifact = synthesize_once(command, output, liberty, "design-a")
    assert second.returncode == 0
    assert artifact.netlist.is_file()
    assert "cached" not in second.stdout


def test_synthesis_rejects_success_without_netlist(tmp_path: Path):
    liberty = tmp_path / "test.lib"
    liberty.write_text("library(test) {}\n")
    with pytest.raises(FileNotFoundError, match="expected netlist"):
        synthesize_once(["true"], tmp_path / "synthesis", liberty, "design-a")


def test_corrupt_manifest_is_a_cache_miss(tmp_path: Path):
    liberty = tmp_path / "test.lib"
    liberty.write_text("library(test) {}\n")
    output = tmp_path / "synthesis"
    command = ["sh", "-c", "printf 'module top; endmodule\\n' > mapped.v"]

    synthesize_once(command, output, liberty, "design-a")
    (output / "synthesis.manifest").write_text("{not valid json\n")

    result, _ = synthesize_once(command, output, liberty, "design-a")
    assert result.returncode == 0
    assert result.stdout != "cached synthesis\n"
