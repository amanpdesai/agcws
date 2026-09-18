import pytest

from agcws.pipeline.storage import write
from analysis.flash_matrix_secondary import derive
from analysis.publish_baseline_matrix import ARMS
from analysis.publish_flash_matrix import (
    ARM,
    ReplayMeter,
    common_valid,
    inference,
    summarize_prefixes,
)


def test_inference_excludes_flat_control_and_uses_seed_units():
    cells = []
    for seed in (1, 2):
        for arm in (ARM, *ARMS):
            for target in ('shape-a', 'shape-b', 'flat_control'):
                auc = (10000 if arm == ARM else 0) if target == 'flat_control' else (1 if arm == ARM else 2)
                cells.append({'seed': seed, 'arm': arm, 'target': target, 'auc': auc})
    rows = inference(cells)
    assert len(rows) == 3
    for row in rows:
        assert row['seed_mean_differences'] == [-1, -1]
        assert row['exact_sign_flip_p'] == .5


def test_equal_valid_counts_do_not_treat_invalid_as_measurements():
    a = [{'valid': False, 'loss': None}, {'valid': True, 'loss': .3}, {'valid': True, 'loss': .01}]
    b = [{'valid': True, 'loss': .2}]
    result = common_valid(a, b)
    assert result['valid_evaluations'] == 1
    assert result['flash_best_error'] == .3
    assert result['baseline_best_error'] == .2
    assert common_valid([], b)['flash_best_error'] is None


def test_prefixes_carry_forward_only_after_a_solve():
    history = [{'slot': 1, 'valid': True, 'loss': .2, 'max_bin_error': .4},
               {'slot': 2, 'valid': True, 'loss': .01, 'max_bin_error': .02}]
    rows = summarize_prefixes(history)
    assert rows['128']['charged_slots'] == 2
    assert rows['128']['evaluations_to_target'] == 2
    assert rows['128']['curve'][-1] == .01
    history[-1]['max_bin_error'] = .2
    with pytest.raises(ValueError, match='short trajectory'):
        summarize_prefixes(history)


def test_replay_rejects_different_payload(tmp_path):
    write(tmp_path/'input.json', {'identity': {}, 'payload': 'privileged'})
    write(tmp_path/'response.json', {})
    write(tmp_path/'request_started.json', {})
    with pytest.raises(ValueError, match='prior-history'):
        ReplayMeter().call(tmp_path, ARM, 'actual history', {}, {})


def test_secondary_zero_solves_and_invalid_prefix_diagnostic():
    from analysis.publish_baseline_matrix import DESIGNS

    base_cell = {'target': 'shape', 'seed': 1, 'curve': [.2]*128, 'solved': False,
                 'evaluations_to_target': 128}
    agent = {**base_cell, 'arm': ARM, 'costs': {'known_usage_estimate_usd': 1,
                                              'reconciled_conservative_liability_usd': 2}}
    flash = {'designs': {d: {'cells': [agent], 'equal_valid_evaluations': [
        {'target': 'shape', 'baseline': a, 'valid_evaluations': 0,
         'flash_best_error': None, 'baseline_best_error': None} for a in ARMS]} for d in DESIGNS}}
    baseline = {'designs': {d: {'cells': [{**base_cell, 'arm': a} for a in ARMS]} for d in DESIGNS}}
    result = derive(flash, baseline)['aes']
    assert result['cost_per_solve']['nonflat']['conservative_liability_per_solve_usd'] is None
    assert result['nonflat_equal_valid_diagnostic']['phase-ga']['zero_common_valid_cells'] == 1
    assert result['nonflat_budget_slices']['16'][ARM]['mean_auc'] == pytest.approx(3)
