from pathlib import Path

import pytest

from agcws.nodes.simulate import run_simulator


def test_simulator_requires_waveform(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="expected waveform"):
        run_simulator(["true"], tmp_path, timeout_s=1)


def test_simulator_returns_artifact(tmp_path: Path):
    command = ["sh", "-c", "printf '$enddefinitions $end\\n' > activity.vcd"]
    _, artifact = run_simulator(command, tmp_path, timeout_s=1)
    assert artifact.waveform == tmp_path / "activity.vcd"
    assert artifact.stdout.is_file()
    assert artifact.stderr.is_file()
