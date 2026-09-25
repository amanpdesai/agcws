from pathlib import Path

import pytest

from agcws.core.contracts import SimResult, ValidityStage
from agcws.designs.aes import AESAdapter
from agcws.designs.validation import validate_workload
from agcws.evaluation.activity.generic import ActivityArtifact
from agcws.evaluation.power.runner import evaluate_power
from agcws.evaluation.simulation.runner import run_simulator
from agcws.evaluation.synthesis.runner import NetlistArtifact


@pytest.mark.parametrize("result,stage", [
    (SimResult(False, True, True, 16), ValidityStage.FUNCTIONAL),
    (SimResult(True, False, True, 16), ValidityStage.FUNCTIONAL),
    (SimResult(True, True, False, 16), ValidityStage.FUNCTIONAL),
    (SimResult(True, True, True, 1), ValidityStage.USEFUL_WORK),
])
def test_runtime_gate_rejects_incomplete_or_idle_work(result, stage):
    workload = {"operations": [{"op": "configure"}, {"op": "encrypt", "blocks": 16}]}
    verdict = validate_workload(AESAdapter(), workload, result)
    assert not verdict.valid and verdict.stage is stage


def test_successful_process_without_power_report_cannot_return_profile(tmp_path):
    netlist, liberty, manifest, activity = [tmp_path / name for name in
                                         ("mapped.v", "cells.lib", "manifest.json", "activity.saif")]
    for path in (netlist, liberty, manifest, activity):
        path.write_text("fixture")
    with pytest.raises(FileNotFoundError, match="expected report"):
        evaluate_power(["true"], NetlistArtifact(netlist, liberty, manifest),
                       ActivityArtifact(activity), tmp_path / "power")


def test_simulator_failure_is_not_returned_as_a_valid_artifact(tmp_path: Path):
    with pytest.raises(RuntimeError, match="simulator failed"):
        run_simulator(["sh", "-c", "echo broken >&2; exit 3"], tmp_path, 5)
    assert (tmp_path / "sim.stderr").read_text().strip() == "broken"
