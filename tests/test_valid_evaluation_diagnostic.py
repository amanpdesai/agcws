import pytest

from analysis.valid_evaluation_diagnostic import mean_auc, valid_curve


def test_invalid_slots_do_not_enter_valid_axis():
    rows = [{'validity': {'valid': valid}, 'loss': loss}
            for valid, loss in [(False, None), (True, 0.4), (False, None),
                                (True, 0.1), (True, 0.3)]]
    assert valid_curve(rows) == [0.4, 0.1, 0.1]
    assert mean_auc(valid_curve(rows), 3) == pytest.approx(0.175)


def test_missing_support_is_not_imputed():
    with pytest.raises(ValueError, match='insufficient'):
        mean_auc([0.1], 2)
    with pytest.raises(ValueError, match='invalid loss'):
        valid_curve([{'validity': {'valid': True}, 'loss': None}])
