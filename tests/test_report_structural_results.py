import itertools

import pytest

from analysis.report_structural_results import render
from analysis.structural_inference import compare


def reports():
    spec = {'phase': 'held-out', 'selected_family': 'best-eight', 'designs': ['aes', 'dma'],
            'targets': ['random_300', 'random_301'], 'seeds': list(range(400, 410)),
            'budget': 32, 'batch_size': 4,
            'policies': ['random', 'evolutionary', 'edit-agent', 'edit-hybrid']}
    rows = [{'design_key': d, 'reference_name': t, 'seed': s, 'policy_alias': p,
             'auc_best_so_far': 1.0, 'solved': False, 'right_censored': True,
             'evaluations_to_target': 32, 'valid_trials': 32, 'validity_failures': {},
             'est_cost_usd': 0, 'unknown_usage_batches': 0,
             'ledger_timing_s': {'wall_clock_s': 1, 'generation_wall_clock_s': 0}}
            for d, t, s, p in itertools.product(spec['designs'], spec['targets'], spec['seeds'], spec['policies'])]
    heldout = {'audited_cells': 160, 'audited_slots': 5120, 'spec': spec, 'rows': rows,
               'inference': compare(rows, spec)}
    cases = [{'design': d, 'target': t, 'policy': p, 'validation_status': 'matched',
              'replay_id': 'fixture', 'proposal_source': 'initialization'}
             for d, t, p in itertools.product(spec['designs'], spec['targets'], spec['policies'])]
    validation = {'selected_cases': 16, 'matched_cases': 16,
                  'unique_replays': {'fixture': {'comparison': {'dynamic_power_w': 0.004,
                                    'annotated_pins': 100, 'unannotated_pins': 2}}}, 'cases': cases,
                  'validation_wall_clock_s': 1}
    return heldout, validation


def test_primary_precedes_secondary_and_limits_survive():
    heldout, validation = reports()
    report = render(heldout, validation)
    assert report.index('## Primary endpoint') < report.index('## Validity, cost and runtime')
    assert 'Nonsignificance is not equivalence' in report
    assert '160 cells / 5120 proposed slots' in report
    assert '0/20' in report and '32.00' in report
    assert 'initialization | 4.000000 | 100/102' in report
    assert 'It is not temporal target error' in report


def test_incomplete_panel_cannot_be_rendered_as_complete():
    heldout, validation = reports()
    heldout['audited_cells'] = 159
    with pytest.raises(ValueError, match='complete held-out'):
        render(heldout, validation)
