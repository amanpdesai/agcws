import pytest

from analysis.matched_power import parse_report


def test_dynamic_excludes_leakage():
    result = parse_report('Total 1 2 3 6\nvcd 10\nunannotated 2\n')
    assert result['dynamic_power_w'] == 3
    assert result['total_power_w'] == 6
    assert result['unannotated_pins'] == 2


@pytest.mark.parametrize('text', ['Total nan 2 3 6\nvcd 10\nunannotated 0',
                                 'Total 1 2 3 9\nvcd 10\nunannotated 0',
                                 'Total 1 2 3 6', 'Total -1 2 3 4\nvcd 10\nunannotated 0'])
def test_missing_nonfinite_negative_or_inconsistent_reports_fail(text):
    with pytest.raises(ValueError):
        parse_report(text)
