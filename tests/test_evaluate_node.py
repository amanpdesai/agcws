from pathlib import Path

import pytest

from agcws.nodes.activity import ActivityArtifact
from agcws.nodes.evaluate import evaluate_power
from agcws.nodes.synthesize import NetlistArtifact


def artifacts(tmp_path: Path) -> tuple[NetlistArtifact, ActivityArtifact]:
    (tmp_path / "mapped.v").write_text("module top; endmodule\n")
    (tmp_path / "cells.lib").write_text("library(test) {}\n")
    (tmp_path / "activity.saif").write_text("(SAIFILE)\n")
    return (
        NetlistArtifact(tmp_path / "mapped.v", tmp_path / "cells.lib", tmp_path / "manifest.json"),
        ActivityArtifact(tmp_path / "activity.saif"),
    )


def test_evaluate_power_rejects_command_failure(tmp_path):
    with pytest.raises(RuntimeError, match="OpenSTA failed"):
        evaluate_power(["sh", "-c", "echo failed >&2; exit 7"], *artifacts(tmp_path), tmp_path / "run")


def test_evaluate_power_rejects_missing_report(tmp_path):
    with pytest.raises(FileNotFoundError, match="expected report"):
        evaluate_power(["true"], *artifacts(tmp_path), tmp_path / "run")


def test_evaluate_power_parses_report(tmp_path):
    output = tmp_path / "run"
    output.mkdir()
    (output / "power.rpt").write_text("Total Power = 1.25e-03\n")
    _, profile = evaluate_power(["true"], *artifacts(tmp_path), output)
    assert profile.valid
    assert profile.mean_power == pytest.approx(0.00125)


def test_command_timeout_returns_structured_result(tmp_path):
    from agcws.nodes.commands import run_command
    result = run_command(["sh", "-c", "sleep 1"], cwd=tmp_path, timeout_s=0.01)
    assert result.returncode == 124
    assert "timed out" in result.stderr
