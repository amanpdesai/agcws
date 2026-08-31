import pytest

from agcws.analysis.metrics import best_so_far_auc, evaluations_to_target, summarize_run


def test_auc_uses_proposal_index_and_pads_to_budget():
    assert best_so_far_auc([1.0, 0.5, 0.0], budget=5) == pytest.approx(1.0)


def test_auc_treats_invalid_prefix_as_worst_normalized_error():
    assert best_so_far_auc([float("inf"), 0.5, 0.25]) == pytest.approx(1.125)


def test_unsolved_runs_are_right_censored_at_budget():
    result = summarize_run([0.8, 0.7], 0.05, budget=4)
    assert result == {
        "budget": 4,
        "auc_best_so_far": pytest.approx(2.15),
        "solved": False,
        "evaluations_to_target": 4,
        "right_censored": True,
    }


def test_evaluations_to_target_is_one_based():
    assert evaluations_to_target([0.8, 0.05], 0.05) == 2
