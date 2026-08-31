import pytest

from agcws.analysis.aggregate import bootstrap_mean_ci


def test_bootstrap_ci_is_reproducible():
    first = bootstrap_mean_ci([1, 2, 3, 4], samples=100, seed=11)
    second = bootstrap_mean_ci([1, 2, 3, 4], samples=100, seed=11)
    assert first == second
    assert first["mean"] == pytest.approx(2.5)
    assert first["lower"] <= first["mean"] <= first["upper"]
