from pathlib import Path

from agcws.nodes.evaluator import EvaluationRequest, EvaluationResult


def test_request_defaults_to_explicit_rtl_proxy():
    request = EvaluationRequest(workload={"operations": []})
    assert request.fidelity == "rtl_activity"


def test_result_keeps_fidelity_and_artifact_provenance():
    result = EvaluationResult(
        workload={"id": 1}, profile=None, valid=False,
        fidelity="gate_level", failure_stage="FUNCTIONAL",
        artifacts={"vcd": str(Path("out/candidate.vcd"))},
        provenance={"netlist_sha256": "abc"},
    )
    assert result.fidelity == "gate_level"
    assert result.artifacts["vcd"].endswith("candidate.vcd")
    assert result.provenance["netlist_sha256"] == "abc"
