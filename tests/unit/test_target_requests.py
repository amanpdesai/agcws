import pytest

from agcws.studies.targets import diagnostics, distance, qualify, requests


def test_distinct_requests_and_separate_control():
    for split in ("development", "confirmation"):
        bank = requests(10, 110, split=split)
        assert len(bank) == 9
        assert sum(r["control"] for r in bank) == 1
        assert len({tuple(r["rates"]) for r in bank}) == 9
        assert not any(r["qualified"] for r in bank)
        assert all(r["constant_floor"] > 0.1 for r in bank if not r["control"])


def test_constant_floor_is_least_squares_constant():
    rates = [0, 0, 0, 0, 2, 2, 2, 2]
    assert diagnostics(rates, 2)["constant_floor"] == 0.5
    assert distance(rates, [1] * 8, 2) < distance(rates, [0.5] * 8, 2)


def test_witness_required_and_request_not_replaced():
    request = requests(10, 110, split="confirmation")[0]
    kwargs = dict(scale=100, tolerance=0.1, nonflat_margin=0.05)
    assert qualify(request, {"valid": True, "rates": request["rates"]}, **kwargs)["qualified"]
    assert not qualify(request, {"valid": False, "rates": None}, **kwargs)["qualified"]
    assert not qualify(request, {"valid": True, "rates": [50] * 8}, **kwargs)["qualified"]


@pytest.mark.parametrize("values", [[1] * 7, [float("nan")] * 8, [-1] * 8, [True] * 8])
def test_invalid_vectors_rejected(values):
    with pytest.raises(ValueError):
        diagnostics(values, 1)
