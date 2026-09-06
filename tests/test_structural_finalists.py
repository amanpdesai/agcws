from analysis.select_structural_finalists import choose


def trial(valid, loss, attempts):
    return {'validity': {'valid': valid}, 'loss': loss, 'evaluation_attempts': attempts}


def test_first_best_valid_trial_and_actual_evaluator_index():
    rows = [trial(False, None, 0), trial(False, None, 1), trial(True, 0.4, 1),
            trial(True, 0.1, 1), trial(True, 0.1, 1)]
    index, evaluator, best = choose(rows)
    assert index == 3 and evaluator == 2 and best is rows[3]


def test_no_valid_trial_does_not_substitute_a_seed():
    assert choose([trial(False, None, 0)]) is None
