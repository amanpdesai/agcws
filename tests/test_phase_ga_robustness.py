import pytest

from analysis.accounting_math import paired
from analysis.phase_ga_robustness import aggregate, holm


def test_two_contrast_resolution_floor_is_explicit():
    p = paired([-1.0] * 6)["two_sided_exact_sign_flip_p"]
    assert p == 0.03125
    assert holm({"first": p, "second": 0.9}) == {"first": 0.0625, "second": 0.9}
    assert holm({"first": p, "second": p}) == {"first": 0.0625, "second": 0.0625}


def test_aggregate_pairs_seeds_not_eighteen_independent_targets():
    cells = []
    for seed in range(6):
        for target in range(3):
            for arm, value in (("pro-4096", 1), ("phase-ga", 2), ("phase-random", 3)):
                cells.append(
                    {
                        "seed": seed,
                        "target": target,
                        "arm": arm,
                        "prefixes": {
                            str(n): {
                                "auc": value + seed / 10,
                                "mean_auc": (value + seed / 10) / (n - 1),
                                "solved": arm == "pro-4096",
                                "evaluations_to_target": 4 if arm == "pro-4096" else n,
                                "final_loss": 0.01 if arm == "pro-4096" else 0.2,
                                "valid_slots": n,
                            }
                            for n in (16, 32, 64, 128)
                        },
                    }
                )
    budgets, contrasts = aggregate(cells, list(range(6)))
    assert budgets["128"]["phase-ga"]["cells"] == 18
    assert budgets["128"]["phase-ga"]["mean_censored_slots"] == 128
    assert budgets["128"]["pro-4096"]["solves"] == 18
    for contrast in contrasts.values():
        assert contrast["seed_differences"] == pytest.approx([-1.0] * 6)
        assert contrast["holm_two_contrasts_p"] == 0.0625
