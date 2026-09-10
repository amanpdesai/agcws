import random

import pytest

from experiments.ibex_depth_v1.model import settings
from experiments.ibex_temporal_v3.program import canonical, random_program
from experiments.nonflat_temporal_v1.audit import inference
from experiments.nonflat_temporal_v1.study import cpu_candidates
from experiments.nonflat_temporal_v1.targets import select
from experiments.temporal_scaling_v1.baselines import phase_random


def witness(slot, rates, valid=True):
    return {"slot": slot, "rates": rates, "valid": valid, "cache_id": str(slot)}


def test_selection_is_first_qualifying_not_maximum_difficulty():
    rows = [witness(1, [0, 0, 0, 0, 4, 4, 4, 4]), witness(2, [0, 8] * 4)]
    assert select(rows, 10, count=1)[0]["witness_slot"] == 1


def test_flat_and_invalid_are_excluded_without_replacements():
    with pytest.raises(ValueError, match="qualification failed"):
        select([witness(1, [4] * 8), witness(2, [0, 10] * 4, False)], 10, count=1)


def test_separation_skips_duplicates_and_retains_order():
    a, b = [0, 10] * 4, [10, 0] * 4
    result = select([witness(1, a), witness(2, a), witness(3, b)], 10, count=2)
    assert [t["witness_slot"] for t in result] == [1, 3]


@pytest.mark.parametrize("rates", [[float("nan")] * 8, [-1] * 8, [1] * 7])
def test_bad_rates_fail_loudly(rates):
    with pytest.raises(ValueError):
        select([witness(1, rates)], 10, count=1)


def test_shared_initialization_and_untuned_phase_random():
    left, right = random.Random(1200), random.Random(1200)
    assert cpu_candidates(left, 0) == [random_program(right) for _ in range(2)]
    for offset in range(2, 128, 2):
        actual = cpu_candidates(left, offset)
        assert actual == [phase_random(right, offset + j + 1) for j in range(2)]
        for p in actual:
            assert canonical(p) == p


def test_exact_sign_flip_resolution_and_symmetry():
    result = inference([-1] * 6)
    assert result["two_sided_exact_sign_flip_p"] == 2 / 64
    assert result["seed_bootstrap_95_percentile"] == [-1, -1]
    assert inference([1] * 6)["two_sided_exact_sign_flip_p"] == 2 / 64
    assert inference([0] * 6)["two_sided_exact_sign_flip_p"] == 1


def test_incomplete_seed_panel_has_no_inference():
    with pytest.raises(ValueError):
        inference([1] * 5)


def test_selected_model_settings_unchanged():
    assert settings("pro-4096") == {
        "model": "gemini-2.5-pro",
        "thinking_budget": 4096,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 16384,
    }
