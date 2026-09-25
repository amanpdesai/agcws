import pytest

from agcws.evaluation.power.windows import reconstruction


def test_failed_reconstruction_requires_proof_not_legacy_exception():
    full, weighted = .0027062583084507042, .0026911617249380454
    assert not reconstruction(full, weighted)['accepted_estimate']
    with pytest.raises(ValueError, match='unknown reconstruction policy'):
        reconstruction(full, weighted, policy='ibex-10ns-estimate-v1',
                       top='ibex_top', period_s=1e-8)
    assert reconstruction(full, weighted)['relative_error'] == pytest.approx(.0055784, rel=1e-5)


@pytest.mark.parametrize('top,period', [('aes', 1e-8), ('ibex_top', 1e-7)])
def test_exception_cannot_change_design_or_clock(top, period):
    with pytest.raises(ValueError, match='approved design'):
        reconstruction(1, .9, policy='slew-verified-v1', top=top, period_s=period)


def test_nonfinite_values_never_accepted():
    with pytest.raises(ValueError, match='invalid'):
        reconstruction(1, float('nan'), policy='slew-verified-v1',
                       top='ibex_top', period_s=1e-8)
