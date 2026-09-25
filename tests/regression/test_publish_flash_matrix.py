import pytest

from agcws.core.storage import write
from agcws.reporting.baselines import ARMS
from agcws.reporting.models import ARM, ReplayMeter, common_valid, inference, summarize_prefixes
from agcws.reporting.secondary import derive


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


def test_historical_api_errors_replay_without_execution_fallback(tmp_path, monkeypatch):
    from agcws.reporting.models import replay_model_batch
    from agcws.search.dispatch import Policy
    from agcws.search.providers.schema import provenance

    policy = Policy(ARM, 1, {'domain': 'ibex-temporal', 'batch_size': 2,
        'budget': 128, 'scale': 1, 'tolerance': .05}, [0]*8, {}, None)
    monkeypatch.setattr(policy.backend, 'payload', lambda *args: 'frozen history')
    identity = {'first_slot': 3}
    response = {'identity': identity, 'schema_provenance': provenance({}),
                'usage_unknown': True, 'api_error': 'archived 503',
                'raw_text': '', 'model_version': None}
    write(tmp_path/'input.json', {'identity': identity, 'payload': 'frozen history'})
    write(tmp_path/'response.json', response)
    write(tmp_path/'request_started.json', {
        'identity': identity, 'schema_provenance': provenance({})})
    write(tmp_path/'decoded.json', policy.backend.decode('', 2))
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    proposals = replay_model_batch(policy, [{}, {}], tmp_path, identity)
    assert len(proposals) == 2
    assert all(p['api_error'] == 'archived 503' for p in proposals)
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


def test_secondary_zero_solves_and_invalid_prefix_diagnostic():
    from agcws.reporting.baselines import DESIGNS

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
