import gzip
import json
import math
from pathlib import Path

import pytest

from agcws.pipeline.evidence import materialize
from analysis.accounting_audit import audit, canonical, equivalent, program_id
from analysis.accounting_math import charge, paired, prefix, rms


def row(slot, loss):
    return {"slot": slot, "loss": loss, "valid": loss is not None}


def test_trapezoid_includes_charged_failure_and_has_no_slot_zero():
    result = prefix([row(1, 0.5), row(2, None), row(3, 0.2)], 3, 0.2)
    assert result["curve"] == [0.5, 0.5, 0.2]
    assert result["auc"] == pytest.approx(0.85)
    assert result["evaluations_to_target"] == 3
    assert result["right_censored"] is False


def test_invalid_prefix_does_not_clip_subsequent_valid_loss():
    result = prefix([row(1, None), row(2, 2), row(3, 1.5)], 3, 0.1)
    assert result["curve"] == [1, 2, 1.5]
    assert result["auc"] == 3.25
    assert result["right_censored"] is True
    assert result["evaluations_to_target"] == 3


def test_all_invalid_is_censored_not_dropped():
    result = prefix([row(i, None) for i in range(1, 5)], 4, 0.1)
    assert result["auc"] == 3
    assert result["final_loss"] is None
    assert result["valid_slots"] == 0


@pytest.mark.parametrize(
    "rows",
    [
        [row(2, 0.1), row(3, 0.2)],
        [row(1, 0.1)],
        [row(1, float("nan")), row(2, 0.2)],
        [{"slot": 1, "valid": False, "loss": 0}, row(2, 0.2)],
    ],
)
def test_bad_accounting_fails_closed(rows):
    with pytest.raises(ValueError):
        prefix(rows, 2, 0.1)


def test_integer_counts_and_scale_without_clamping():
    assert rms([10] * 8, [2] * 8, 4) == 2
    assert rms([1, 0, 0, 0, 0, 0, 0, 0], [0] * 8, 1) == pytest.approx(math.sqrt(1 / 8))
    with pytest.raises(ValueError):
        rms([0] * 7, [0] * 8, 1)


def test_exact_test_resolution_and_constant_bootstrap():
    answer = paired([-2] * 6)
    assert answer["mean_difference"] == -2
    assert answer["two_sided_exact_sign_flip_p"] == 0.03125
    assert answer["seed_bootstrap_95_percentile"] == [-2, -2]
    assert paired([0] * 6)["two_sided_exact_sign_flip_p"] == 1
    with pytest.raises(ValueError):
        paired([-1] * 18)


def response():
    return {
        "usage_unknown": False,
        "usage_fields": {
            "prompt_token_count": 100,
            "candidates_token_count": 20,
            "thoughts_token_count": 30,
        },
        "tokens_in": 100,
        "tokens_out": 50,
        "thinking_tokens": 30,
        "estimated_usd": 0.000625,
    }


def test_cost_counts_thinking_once_and_reserves_unknown_usage():
    assert charge(response(), 0.41384) == {
        "known": 0.000625,
        "reserved": 0,
        "input": 100,
        "output": 50,
    }
    assert (
        charge(
            {"usage_unknown": True, "tokens_in": None, "tokens_out": None, "estimated_usd": None},
            0.41384,
        )["reserved"]
        == 0.41384
    )
    bad = response()
    bad["tokens_out"] = 20
    with pytest.raises(ValueError):
        charge(bad, 0.41384)
    bad = response()
    bad["usage_fields"]["prompt_token_count"] = -1
    with pytest.raises(ValueError):
        charge(bad, 0.41384)


def test_cache_key_includes_measurement_and_only_normalizes_integral_numbers():
    a = {"registers": [1.0, 2], "x": 3.5}
    assert canonical(a) == {"registers": [1, 2], "x": 3.5}
    assert program_id(a, "measurement1") == program_id(canonical(a), "measurement1")
    assert program_id(a, "measurement1") != program_id(a, "measurement2")
    assert program_id(a, "measurement1") != program_id(
        {"registers": [1, 3], "x": 3.5}, "measurement1"
    )


def test_comparison_does_not_hide_boolean_or_missing_fields():
    assert not equivalent(True, 1)
    assert not equivalent({"valid": True}, {"valid": True, "loss": 0})
    assert not equivalent(float("nan"), float("nan"))
    assert equivalent(0.1, 0.1 + 1e-12)


def test_full_audit_detects_tampered_score_in_isolated_restoration(tmp_path):
    repo = Path.cwd()
    view = materialize(repo, tmp_path / "review", ["nonflat_temporal_v1"])
    root = view / "results/nonflat_temporal_v1"
    path = root / "panel/target_0/1200/pro-4096/batches/005/trials.json.gz"
    assert not path.is_symlink()
    rows = json.loads(gzip.decompress(path.read_bytes()))
    rows[0]["loss"] += 0.2
    path.write_bytes(gzip.compress(json.dumps(rows).encode()))
    result = audit(root, repo)
    labels = {d["check"] for d in result["discrepancies"]}
    assert "loss_from_measured_counts" in labels
    assert "complete_matches_batches" in labels
