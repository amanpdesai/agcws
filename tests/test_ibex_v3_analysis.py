import copy
import itertools

import pytest

from agcws.policies.source_context import build_bundle
from agcws.provenance import file_sha256
from analysis.ibex_temporal_v3 import check_feedback, describe_panel, verify_bundle
from experiments.ibex_temporal_v3.feedback import CLASSES


def feedback():
    return {
        "begin_tick": 10,
        "end_tick": 400010,
        "cycles_per_bin": 25000,
        "retired_classes": [{k: int(k == "alu") for k in CLASSES} for _ in range(8)],
        "retired_per_bin": [1] * 8,
        "cycles_without_retirement": [24999] * 8,
    }


def test_feedback_audit_catches_mixed_windows_and_bad_counts():
    data = feedback()
    check_feedback(data, {"begin_tick": 10, "end_tick": 400010})
    with pytest.raises(ValueError, match="interval"):
        check_feedback(data, {"begin_tick": 12, "end_tick": 400012})
    broken = copy.deepcopy(data)
    broken["retired_per_bin"][0] = 10
    with pytest.raises(ValueError, match="arithmetic"):
        check_feedback(broken, data)


def test_factorial_contrasts_and_per_run_coverage():
    means = {
        "random": 1,
        "coverage": 2,
        "agent-base": 4,
        "agent-context": 3,
        "agent-correction": 2,
        "agent-combined": 0.5,
    }
    manifest = {
        "targets": {"a": {}, "b": {}},
        "seeds": [1, 2],
        "policies": list(means),
        "budget": 2,
        "shared_initial_slots": 1,
        "scale": 10,
    }
    cells = []
    for target, seed, policy in itertools.product(
        manifest["targets"], manifest["seeds"], means
    ):
        summary = {
            "target": target,
            "seed": seed,
            "policy": policy,
            "auc": means[policy],
            "final_loss": 0.2,
            "solved": False,
            "evaluations_to_target": 2,
            "est_cost_usd": 0,
            "unknown_usage_batches": 0,
        }
        trials = [
            {
                "slot": i,
                "valid": True,
                "stage": None,
                "rates": [1] * 8,
                "feedback": feedback(),
                "tokens_in": 3,
                "tokens_out": 2,
            }
            for i in (1, 2)
        ]
        cells.append((summary, trials))
    result = describe_panel(manifest, cells)
    assert result["descriptive_auc_contrasts"]["interaction"] == -0.5
    assert result["descriptive_auc_contrasts"]["context_without_correction"] == -1
    for report in result["policies"].values():
        assert report["mean_behavior_cells_per_run"] == 1
        assert "grid_profiles" not in report
        assert report["generated_slots"] == 4
    with pytest.raises(ValueError, match="incomplete"):
        describe_panel(manifest, cells[:-1])


def test_bundle_audit_checks_unselected_sources_too(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "rtl.sv").write_text("module m; endmodule\n")
    target = tmp_path / "bundle"
    build_bundle(source, target, ["rtl.sv"])
    digest = file_sha256(target / "manifest.json")
    verify_bundle(target, digest)
    path = target / "rtl.sv"
    path.chmod(0o644)
    path.write_text("changed")
    with pytest.raises(ValueError, match="source differs"):
        verify_bundle(target, digest)
