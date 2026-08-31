import pytest

from agcws.analysis.rank_agreement import bootstrap_rank_ci, rank_agreement


def test_rank_agreement_is_one_for_identical_order():
    result = rank_agreement([("a", 1), ("b", 2), ("c", 3)], [("a", 10), ("b", 20), ("c", 30)])
    assert result["shared_workloads"] == 3
    assert result["spearman_rho"] == pytest.approx(1.0)


def test_rank_agreement_requires_shared_corpus():
    with pytest.raises(ValueError):
        rank_agreement([("a", 1)], [("a", 2)])


def test_bootstrap_rank_ci_is_deterministic():
    left = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
    right = [("a", 10), ("b", 20), ("c", 30), ("d", 40)]
    first = bootstrap_rank_ci(left, right, samples=100, seed=4)
    assert first == bootstrap_rank_ci(left, right, samples=100, seed=4)
    assert first["mean"] == pytest.approx(1.0)
