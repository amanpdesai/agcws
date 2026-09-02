import pytest

from agcws.analysis.inference import (holm_bonferroni,
                                       paired_permutation_pvalue,
                                       rank_biserial_effect)


def test_paired_permutation_is_exact_and_deterministic():
    assert paired_permutation_pvalue([3, 4, 5], [1, 2, 3]) == 0.25
    assert paired_permutation_pvalue([1, 2], [1, 2]) == 1.0


def test_inference_rejects_unpaired_samples():
    with pytest.raises(ValueError):
        paired_permutation_pvalue([1], [1, 2])


def test_holm_preserves_input_order():
    assert holm_bonferroni([0.04, 0.001, 0.02]) == [0.04, 0.003, 0.04]


def test_rank_biserial_effect():
    assert rank_biserial_effect([3, 4, 5], [1, 2, 3]) == 1.0


def test_rank_biserial_effect_reports_tie():
    assert rank_biserial_effect([1, 2], [1, 2]) == 0.0
