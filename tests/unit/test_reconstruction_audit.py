"""Regression coverage for separating counted activity from clipped power."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agcws.evaluation.power.reconstruction_audit import (
    compare,
    instrument_tcl,
    slew_proof,
    unclipped_switching,
)
from agcws.evaluation.power.windows import reconstruction


def test_count_additivity_does_not_imply_clipped_power_additivity():
    # Whole density is 3; two equal bins have densities 1 and 5. Cap is 4.
    full = {'counts': {'gate/Y': 6}, 'leaves': {'gate': 6.0}}
    bins = [{'counts': {'gate/Y': 1}, 'leaves': {'gate': 2.0}},
            {'counts': {'gate/Y': 5}, 'leaves': {'gate': 8.0}}]
    result = compare(full, bins, [1, 1])
    assert result['count_mismatches'] == {}
    assert result['weighted_w'] == 5.0
    assert result['full_w'] == 6.0
    corrected = unclipped_switching([6, 1, 5], [2, 1, 1], [3, 1, 4], [6, 2, 8])
    assert corrected['clipped'] == [False, False, True]
    assert corrected['unclipped_switching_w'] == [6, 2, 10]


def test_whole_and_burst_can_both_be_clipped():
    result = unclipped_switching([12, 2, 10], [2, 1, 1], [4, 2, 4], [8, 4, 8])
    assert result['clipped'] == [True, False, True]
    assert result['unclipped_switching_w'] == [12, 4, 20]


def test_count_error_is_not_misclassified_as_clipping():
    with pytest.raises(ValueError, match='transition counts'):
        unclipped_switching([7, 1, 5], [2, 1, 1], [3, 1, 4], [6, 2, 8])


def test_varying_load_is_not_silently_corrected():
    with pytest.raises(ValueError, match='coefficient differs'):
        unclipped_switching([6, 1, 5], [2, 1, 1], [3, 1, 4], [6, 2, 9])


def test_missing_pin_coverage_is_rejected():
    with pytest.raises(ValueError, match='counts coverage'):
        compare({'counts': {'a': 1}, 'leaves': {'gate': 1}},
                [{'counts': {}, 'leaves': {'gate': 1}}], [1])


def test_unequal_durations_and_zero_activity():
    result = unclipped_switching([9, 0, 9], [4, 1, 3], [2.25, 0, 3], [4.5, 0, 6])
    assert result['clipped'] == [False, False, False]
    assert result['unclipped_switching_w'] == [4.5, 0, 6]


@pytest.mark.parametrize('duration', [0, -1, float('nan'), float('inf')])
def test_invalid_duration(duration):
    with pytest.raises(ValueError, match='duration'):
        unclipped_switching([6, 1, 5], [2, duration, 1], [3, 1, 4], [6, 2, 8])


def proof_fixture(tmp_path, *, counts=(6, 1, 5), densities=(3e6, 1e6, 4e6),
                  powers=(6e-6, 2e-6, 8e-6), slews=(250, 250, 250),
                  caps=(2e-12/1.62, 2e-12/1.62, 2e-12/1.62), unaffected=(1e-6, 1e-6, 1e-6),
                  origin='vcd'):
    paths, rows = [], []
    for i in range(3):
        path = tmp_path / f'{i}.rpt'
        path.write_text(
            f'read_vcd: gate/Y transitions {float(counts[i]):.1f} activity 0 duty 0.5\n'
            'read_vcd: other/Y transitions 0.0 activity 0 duty 0.5\n'
            'SLEW_AUDIT_VERSION slew-verified-v1\n'
            f'SLEW_LEAF gate {powers[i]}\n'
            f'SLEW_LEAF other {unaffected[i]}\n'
            f'SLEW_PIN gate/Y gate {densities[i]} 0.5 {origin} '
            f'{slews[i]} {slews[i]} {slews[i]} {slews[i]} {caps[i]} {caps[i]}\n'
            # Clock-origin output exercises strict unaffected checking without
            # pretending counted VCD density governs ideal-clock activity.
            'SLEW_PIN other/Y other 1e6 0.5 clock 0 0 0 0 1e-12 1e-12\n'
            f'LEAF_SWITCHING_SUM 2 {powers[i]+unaffected[i]}\n'
            'SLEW_AUDIT_END\n')
        paths.append(path)
        rows.append({'annotated_pins': 2, 'unannotated_pins': 0, 'leaf_count': 2,
                     'leaf_switching_sum_w': powers[i]+unaffected[i]})
    return paths, [1e-6, 1e-6], rows


def test_slew_verified_accepts_explained_native_nonadditivity(tmp_path):
    proof = slew_proof(*proof_fixture(tmp_path))
    assert proof['pass'] and proof['clipped_cells'] == ['gate']
    assert proof['count_mismatch_count'] == 0
    assert proof['unexplained_difference_w'] == pytest.approx(0, abs=1e-20)
    result = reconstruction(7e-6, 6e-6, policy='slew-verified-v1',
                            top='ibex_top', period_s=1e-8, proof=proof)
    assert result['accepted_estimate'] and result['validation_pass']
    assert not result['pass']  # Native additivity remains truthfully false.
    assert not reconstruction(7e-6, 6e-6)['accepted_estimate']


@pytest.mark.parametrize('change,reason', [
    ({'counts': (7, 1, 5)}, 'transition counts'),
    ({'densities': (3e6, 1e6, 3e6)}, 'density not explained'),
    ({'slews': (250, 250, 200)}, 'load/slew'),
    ({'caps': (1e-12, 1e-12, 2e-12)}, 'load/slew'),
    ({'powers': (6e-6, 2e-6, 9e-6)}, 'coefficient'),
    ({'unaffected': (1e-6, 1e-6, 2e-6)}, 'unaffected cell'),
    ({'origin': 'unknown'}, 'unsupported activity'),
])
def test_slew_verified_rejects_unexplained_cases(tmp_path, change, reason):
    proof = slew_proof(*proof_fixture(tmp_path, **change))
    assert not proof['pass']
    assert any(reason in error for error in proof['failures'])


def test_missing_evidence_cannot_pass_even_if_native_power_adds():
    result = reconstruction(1, 1, policy='slew-verified-v1', top='ibex_top', period_s=1e-8)
    assert result['pass'] and not result['accepted_estimate']


def test_incomplete_claim_of_proof_cannot_pass():
    proof = {'version': 'slew-verified-v1', 'pass': True, 'failures': [],
             'count_mismatch_count': 0, 'native_full_w': 1, 'native_weighted_w': .9}
    assert not reconstruction(1, .9, policy='slew-verified-v1', top='ibex_top',
                              period_s=1e-8, proof=proof)['accepted_estimate']


@pytest.mark.parametrize('top,period', [('aes', 1e-8), ('ibex_top', 1e-7)])
def test_slew_policy_cannot_change_design_or_clock(top, period):
    with pytest.raises(ValueError, match='approved design'):
        reconstruction(1, .9, policy='slew-verified-v1', top=top, period_s=period)


def test_proof_cannot_be_reused_for_another_measurement(tmp_path):
    proof = slew_proof(*proof_fixture(tmp_path))
    assert not reconstruction(1, .9, policy='slew-verified-v1', top='ibex_top',
                              period_s=1e-8, proof=proof)['accepted_estimate']


def test_incomplete_report_cannot_pass(tmp_path):
    paths, durations, rows = proof_fixture(tmp_path)
    paths[2].write_text(paths[2].read_text().replace('SLEW_AUDIT_END', ''))
    with pytest.raises(ValueError, match='incomplete'):
        slew_proof(paths, durations, rows)


def test_duplicate_pin_evidence_is_rejected(tmp_path):
    paths, durations, rows = proof_fixture(tmp_path)
    paths[1].write_text(paths[1].read_text() +
                       'read_vcd: gate/Y transitions 1.0 activity 0 duty 0.5\n')
    with pytest.raises(ValueError, match='duplicate counted pin'):
        slew_proof(paths, durations, rows)


def test_native_components_must_reproduce_archive(tmp_path):
    paths, durations, rows = proof_fixture(tmp_path)
    for path, row in zip(paths, rows):
        power = row['leaf_switching_sum_w']
        path.write_text(path.read_text() +
                        f'Total 2e-6 {power} 0 {2e-6+power}\nvcd 2\nunannotated 0\n')
        row.update(internal_power_w=2e-6, switching_power_w=power, leakage_power_w=0,
                   dynamic_power_w=2e-6+power, total_power_w=2e-6+power)
    rows[2]['internal_power_w'] = 3e-6
    with pytest.raises(ValueError, match='native power components'):
        slew_proof(paths, durations, rows)


def test_instrumentation_does_not_change_native_settings():
    script = 'create_clock -period 10 [get_ports clk]\nread_vcd trace.vcd\nreport_power -digits 12\n'
    instrumented = instrument_tcl(script)
    assert 'create_clock -period 10 [get_ports clk]' in instrumented
    assert 'read_vcd trace.vcd' in instrumented
    assert 'report_power -digits 12' in instrumented
    assert 'set_power_activity' not in instrumented


def test_opposite_unaffected_errors_cannot_cancel_into_acceptance(tmp_path):
    paths, durations, rows = proof_fixture(tmp_path, unaffected=(1e-6, 1e-6, 1.5e-6))
    for i, path in enumerate(paths):
        power = 1e-6 if i < 2 else .5e-6
        text = path.read_text().replace(
            'SLEW_AUDIT_END',
            'read_vcd: extra/Y transitions 0.0 activity 0 duty 0.5\n'
            f'SLEW_LEAF extra {power}\n'
            'SLEW_PIN extra/Y extra 1e6 0.5 clock 0 0 0 0 1e-12 1e-12\n'
            'SLEW_AUDIT_END')
        row = rows[i]
        old = f'LEAF_SWITCHING_SUM 2 {row["leaf_switching_sum_w"]}'
        row.update(annotated_pins=3, leaf_count=3,
                   leaf_switching_sum_w=row['leaf_switching_sum_w']+power)
        path.write_text(text.replace(old, f'LEAF_SWITCHING_SUM 3 {row["leaf_switching_sum_w"]}'))
    proof = slew_proof(paths, durations, rows)
    assert abs(proof['unexplained_difference_w']) < 1e-20
    assert not proof['pass']
    assert sum('unaffected cell' in f for f in proof['failures']) == 2


def test_half_transition_counts_preserve_exact_reconstruction(tmp_path):
    proof = slew_proof(*proof_fixture(tmp_path, counts=(6, .5, 5.5),
                                     densities=(3e6, .5e6, 4e6), powers=(6e-6, 1e-6, 8e-6)))
    assert proof['pass'] and proof['count_mismatch_count'] == 0


def test_mult_output_clipping_cannot_be_accepted(tmp_path):
    paths, durations, rows = proof_fixture(tmp_path)
    for path, row in zip(paths, rows):
        path.write_text(path.read_text().replace(
            'SLEW_AUDIT_END',
            'read_vcd: gate/Z transitions 0.0 activity 0 duty 0.5\n'
            'SLEW_PIN gate/Z gate 0 0.5 vcd 0 0 0 0 0 0\nSLEW_AUDIT_END'))
        row['annotated_pins'] = 3
    proof = slew_proof(paths, durations, rows)
    assert not proof['pass']
    assert any('multi-output clipping' in f for f in proof['failures'])


@pytest.mark.parametrize('policy,bad_counts,accepted', [
    ('strict', False, False), ('slew-verified-v1', False, True),
    ('slew-verified-v1', True, False),
])
def test_production_evaluator_policy_integration(tmp_path, monkeypatch, policy, bad_counts, accepted):
    from agcws.evaluation.power import windows
    from agcws.evaluation.power.reconstruction_audit import LIBERTY_SHA256

    reports, _, rows = proof_fixture(tmp_path, counts=(7, 1, 5) if bad_counts else (6, 1, 5))
    synthesis = tmp_path / 'synthesis'
    synthesis.mkdir()
    netlist = synthesis / 'mapped.v'
    netlist.write_text('module ibex_top; endmodule\n')
    liberty = tmp_path / 'lib.lib'
    liberty.write_text('time_unit : "1ns";\n')
    real_sha = windows.sha
    monkeypatch.setattr(windows, 'sha', lambda p: LIBERTY_SHA256 if p == liberty else real_sha(p))
    (synthesis / 'manifest.json').write_text(json.dumps({
        'top': 'ibex_top', 'netlist_sha256': real_sha(netlist), 'liberty_sha256': LIBERTY_SHA256}))
    tool = tmp_path / 'sta'
    tool.touch()
    waveform = tmp_path / 'activity.vcd'
    waveform.touch()
    monkeypatch.setattr(windows.config, 'LIBERTY', liberty)
    monkeypatch.setattr(windows.config, 'OPENSTA', tool)
    grid = {'span': {'timescale_s': 1e-12}, 'clock_period_ticks': 10000,
            'bounds_ticks': [1, 1000001, 2000001], 'durations_ticks': [1000000]*2,
            'durations_s': [1e-6]*2}
    monkeypatch.setattr(windows, 'grid', lambda *args, **kwargs: grid)
    scripts = []

    def run(command, **kwargs):
        if 'input' in kwargs:
            return SimpleNamespace(stdout=f'OpenSTA {windows.PIN[:10]}\n')
        tcl = Path(command[-1])
        scripts.append(tcl.read_text())
        index = {'full': 0, 'bin-0': 1, 'bin-1': 2}[tcl.stem]
        power = rows[index]['leaf_switching_sum_w']
        kwargs['stdout'].write(reports[index].read_text() +
                               f'Total 2e-6 {power} 0 {2e-6+power}\nvcd 2\nunannotated 0\n')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(windows.subprocess, 'run', run)
    out = tmp_path / 'production'
    if accepted:
        result = windows.evaluate(waveform, waveform, synthesis, 'clk', 'dut', 200, out,
                                  reconstruction_policy=policy)
        assert result['switching_reconstruction']['validation_pass']
    else:
        with pytest.raises(ValueError, match='additivity failed'):
            windows.evaluate(waveform, waveform, synthesis, 'clk', 'dut', 200, out,
                             reconstruction_policy=policy)
        result = json.loads((out / 'power.json').read_text())
    assert not result['switching_additivity_pass']
    assert result['full']['leaf_switching_sum_w'] == pytest.approx(7e-6)
    assert result['weighted_leaf_switching_w'] == pytest.approx(6e-6)
    assert result['switching_reconstruction']['accepted_estimate'] is accepted
    assert all(('SLEW_AUDIT_VERSION' in s) == (policy == 'slew-verified-v1') for s in scripts)
