from pathlib import Path
import pytest

from agcws.nodes.simulate import run_simulator


def test_evaluator_composes_runtime_useful_work_gate():
    text = Path("scripts/evaluate_aes_workload.py").read_text()
    assert "validate_result" in text
    assert "SimResult" in text
    assert "allow_invalid" in text
    assert "--allow-invalid" in text
    opensta = Path("scripts/run_opensta_aes.sh").read_text()
    assert "report_activity_annotation" in opensta
    assert "annotation.rpt" in opensta


def test_opensta_result_declares_power_metric():
    text = Path("scripts/evaluate_aes_workload.py").read_text()
    assert '"power_metric": "opensta_total_power_w"' in text


def test_opensta_scripts_have_bounded_runtime():
    for name in ("scripts/run_opensta_aes.sh", "scripts/run_opensta_axi_dma.sh"):
        text = Path(name).read_text()
        assert "AGCWS_OPENSTA_TIMEOUT_S" in text
        assert "timeout --kill-after=5s" in text


def test_simulator_failure_is_not_returned_as_a_valid_artifact(tmp_path):
    with pytest.raises(RuntimeError, match="simulator failed"):
        run_simulator(["sh", "-c", "echo broken >&2; exit 3"], tmp_path, 5)
    assert (tmp_path / "sim.stderr").read_text().strip() == "broken"
