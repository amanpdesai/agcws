from copy import deepcopy

import pytest

from agcws.reporting.power_reference import compare_measurements


def measurement(reference=False):
    bins = [1., 2.] * 4
    activity = dict(domain='test', target='step', target_rates=bins, scale=1.,
                    policy='reference' if reference else 'random', seed=1,
                    max_bin_error=.01, activity_solved=True)
    if reference:
        activity['role'] = 'power_reference'
    return dict(activity=activity, case_id=str(reference), gate_dynamic_power_w=bins,
                pin_annotation_fractions=[1.] * 9,
                power=dict(scope='dut', clock_period_s=1e-8, tool_version='pinned',
                           inputs={'net/mapped.v': 'netlist', 'cells.lib': 'library'},
                           grid={'durations_s': [1e-6] * 8}, switching_additivity_pass=True,
                           windows=[{'dynamic_power_w': p} for p in bins]))


def test_join_uses_fixed_reference_and_keeps_activity_separate():
    reference = measurement(True)
    row = compare_measurements(measurement(), reference)
    assert row['nrmse'] == 0
    assert row['activity_max_bin_error'] == .01
    reference['activity']['activity_solved'] = False
    assert 'descriptive' in compare_measurements(measurement(), reference)['interpretation']


def test_explicit_ibex_estimate_keeps_reconstruction_diagnostic():
    candidate, reference = measurement(), measurement(True)
    for item in (candidate, reference):
        item['activity']['domain'] = 'ibex-temporal'
        item['power']['switching_additivity_pass'] = False
        item['power']['switching_reconstruction'] = {
            'policy': 'ibex-10ns-estimate-v1', 'pass': False,
            'relative_error': .0056, 'accepted_estimate': True}
    with pytest.raises(ValueError, match='additivity'):
        compare_measurements(candidate, reference)
    row = compare_measurements(candidate, reference, allow_legacy_estimate=True)
    assert not row['candidate_switching_reconstruction']['pass']
    candidate['activity']['domain'] = reference['activity']['domain'] = 'dma-temporal'
    with pytest.raises(ValueError, match='additivity'):
        compare_measurements(candidate, reference)


@pytest.mark.parametrize('change', ['netlist', 'duration', 'annotation', 'vector', 'target'])
def test_join_rejects_incompatible_or_corrupt_evidence(change):
    candidate, reference = measurement(), deepcopy(measurement(True))
    if change == 'netlist':
        reference['power']['inputs']['net/mapped.v'] = 'different'
    elif change == 'duration':
        reference['power']['grid']['durations_s'][0] *= 2
    elif change == 'annotation':
        reference['pin_annotation_fractions'][0] = .1
    elif change == 'vector':
        reference['gate_dynamic_power_w'][0] = 99
    else:
        reference['activity']['target'] = 'other'
    with pytest.raises(ValueError):
        compare_measurements(candidate, reference)


def slew_measurement(tmp_path, reference=False):
    from agcws.evaluation.power.reconstruction_audit import slew_proof
    from agcws.evaluation.power.windows import reconstruction

    result = measurement(reference)
    result['activity'].update(domain='ibex-temporal', reconstruction_policy='slew-verified-v1')
    rows, paths = [], []
    for i, (count, density) in enumerate([(24, 3e6), *[(n, d) for _ in range(4)
                                                    for n, d in ((1, 1e6), (5, 4e6))]]):
        power = density * 2e-12
        path = tmp_path / ('full.rpt' if i == 0 else f'bin-{i-1}.rpt')
        path.write_text(
            f'read_vcd: gate/Y transitions {count}.0 activity 0 duty 0.5\n'
            'SLEW_AUDIT_VERSION slew-verified-v1\n'
            f'SLEW_LEAF gate {power}\n'
            f'SLEW_PIN gate/Y gate {density} 0.5 vcd 250 250 250 250 {2e-12/1.62} {2e-12/1.62}\n'
            f'LEAF_SWITCHING_SUM 1 {power}\nSLEW_AUDIT_END\n'
            f'Total 2e-6 {power} 0 {2e-6+power}\nvcd 1\nunannotated 0\n')
        rows.append(dict(leaf_switching_sum_w=power, leaf_count=1, annotated_pins=1,
                         unannotated_pins=0, internal_power_w=2e-6, switching_power_w=power,
                         leakage_power_w=0, dynamic_power_w=2e-6+power, total_power_w=2e-6+power))
        paths.append(path)
    proof = slew_proof(paths, [1e-6]*8, rows)
    diagnostic = reconstruction(rows[0]['leaf_switching_sum_w'], 5e-6, policy='slew-verified-v1',
                                top='ibex_top', period_s=1e-8, proof=proof)
    assert diagnostic['accepted_estimate']
    result['power'].update(full=rows[0], windows=rows[1:], weighted_leaf_switching_w=5e-6,
                           switching_additivity_pass=False, switching_reconstruction=diagnostic,
                           artifact_sha256={p.name: proof['report_sha256'][str(p)] for p in paths})
    result['gate_dynamic_power_w'] = [r['dynamic_power_w'] for r in rows[1:]]
    return result


@pytest.mark.parametrize('domain', ['ibex-temporal', 'redmule-temporal-long'])
def test_report_accepts_matching_checked_slew_proof(tmp_path, domain):
    candidate = slew_measurement(tmp_path)
    candidate['activity']['domain'] = domain
    reference = deepcopy(candidate)
    reference['activity']['role'] = 'power_reference'
    result = compare_measurements(candidate, reference)
    assert result['nrmse'] == 0
    assert not result['candidate_switching_reconstruction']['pass']


@pytest.mark.parametrize('change', ['missing', 'forged_flag', 'stale_totals', 'missing_check',
                                  'unexplained', 'stale_bins', 'stale_report', 'fake_additivity',
                                  'missing_diagnostic'])
def test_report_rejects_forged_stale_or_missing_slew_proof(tmp_path, change):
    candidate = slew_measurement(tmp_path)
    reference = deepcopy(candidate)
    reference['activity']['role'] = 'power_reference'
    diagnostic = candidate['power']['switching_reconstruction']
    proof = diagnostic['proof']
    if change == 'missing':
        diagnostic.pop('proof')
    elif change == 'forged_flag':
        diagnostic['proof'] = {'pass': True}
    elif change == 'stale_totals':
        proof['native_full_w'] *= 2
    elif change == 'missing_check':
        proof['verified_checks'].pop()
    elif change == 'unexplained':
        proof['unexplained_difference_w'] = 1
    elif change == 'stale_bins':
        # Same weighted total cannot hide a proof borrowed from another trace.
        proof['native_windows_w'] = list(reversed(proof['native_windows_w']))
    elif change == 'stale_report':
        proof['report_sha256'][str(tmp_path / 'full.rpt')] = 'f'*64
    elif change == 'fake_additivity':
        candidate['power']['switching_additivity_pass'] = True
        diagnostic.pop('proof')
    else:
        candidate['power'].pop('switching_reconstruction')
        candidate['power']['switching_additivity_pass'] = True
    with pytest.raises(ValueError, match='verified slew proof'):
        compare_measurements(candidate, reference)
