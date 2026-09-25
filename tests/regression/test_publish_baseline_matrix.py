import pytest

from agcws.reporting.baselines import aggregate, close, infer


def cell(seed, arm, auc, solved=False):
    return {'seed': seed, 'arm': arm, 'auc': auc, 'solved': solved,
            'evaluations_to_target': 12 if solved else 128, 'charged_slots': 12 if solved else 128,
            'valid_slots': 10 if solved else 120, 'best_max_bin_error': .03 if solved else .2,
            'internal_surrogate_candidates': 64}


def test_aggregate_keeps_unsolved_and_separate_internal_work():
    result = aggregate([cell(1, 'phase-random', 2, True), cell(2, 'phase-random', 4)])
    assert result['cells'] == 2
    assert result['solved'] == 1
    assert result['mean_auc'] == 3
    assert result['mean_evaluations_to_target_censored'] == 70
    assert result['charged_slots'] == 140
    assert result['internal_surrogate_candidates'] == 128


def test_inference_uses_seeds_not_target_replicates():
    rows = [cell(seed, arm, offset+target) for seed in (1, 2)
            for arm, offset in [('phase-random', 1), ('phase-ga', 2), ('phase-model', 3)]
            for target in range(4)]
    contrasts = infer(rows)
    assert len(contrasts) == 3
    assert contrasts[0]['seed_mean_differences'] == [-1, -1]
    assert contrasts[0]['exact_sign_flip_p'] == .5


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -.1])
def test_metric_mismatch_rejected(value):
    with pytest.raises(ValueError):
        close(.1, value)
