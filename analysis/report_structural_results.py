"""Render audited temporal results, with primary inference before diagnostics."""
import argparse
import json
from pathlib import Path
from statistics import mean

LABELS = {'random': 'Random', 'evolutionary': 'Evolutionary', 'edit-agent': 'Agent',
          'edit-hybrid': 'Hybrid', 'population-evolution': 'Population evolutionary',
          'population-agent': 'Population agent', 'population-hybrid': 'Population hybrid'}


def render(heldout, validation):
    if heldout['audited_cells'] != 160 or heldout['audited_slots'] != 5120:
        raise ValueError('complete held-out study required')
    if validation['selected_cases'] != 16:
        raise ValueError('complete finalist reconciliation required')
    spec, rows = heldout['spec'], heldout['rows']
    text = ['# Frozen structural temporal study', '',
            'Scope: goal-conditioned **activity-profile synthesis**, not established power-profile synthesis.', '',
            (f"The development rule selected the **{spec['selected_family']}** family. The frozen study contains "
            '160 cells / 5120 proposed slots: AES and DMA, two achieved reference profiles, '
            'four policies, ten fresh seeds (400–409), 32 slots per run and batch size four. '
            'Targets are previously observed profiles; fresh seeds do not demonstrate unseen-target generalization.'), '',
            ('AES completes exactly 64 blocks in 6774 clock edges; DMA completes 4096 bytes in 12000 edges. '
            'Every method uses the same bounded schedule grammar and hard validity gates. '
            'Invalid, missing and duplicate proposals consume slots. Initialization is shared.'), '',
            '## Primary endpoint', '',
            ('Mean proposal-counted best-so-far loss AUC, lower is better. Loss is the predeclared '
            'fixed-scale capped NRMSE, not candidate-peak normalization.'), '',
            '| Design | Policy | Mean AUC | Solved | Capped evaluations-to-target | Valid slots |',
            '|---|---|---:|---:|---:|---:|']
    for design in spec['designs']:
        for policy in spec['policies']:
            cells = [r for r in rows if r['design_key'] == design and r['policy_alias'] == policy]
            if len(cells) != 20:
                raise ValueError('incomplete design/policy panel')
            text.append(f"| {design.upper()} | {LABELS[policy]} | {mean(r['auc_best_so_far'] for r in cells):.5f} "
                        f"| {sum(r['solved'] for r in cells)}/20 "
                        f"| {mean(r['evaluations_to_target'] for r in cells):.2f} "
                        f"| {sum(r['valid_trials'] for r in cells)}/640 |")
    text += ['', ('Unsolved runs remain right-censored at 32; the capped value is not an estimate '
             'of time to eventual success.'), '', '## Paired inference', '',
             ('Two target differences are averaged within each seed, leaving ten seed units. '
             'Intervals are pointwise 95% bootstrap intervals (10,000 replicates). Exact two-sided '
             'sign flips use joint Holm correction over eight comparisons. '
             'Nonsignificance is not equivalence or proof of parity.'), '',
             '| Design | Method vs baseline | AUC difference | 95% interval | Holm p | Superiority supported |',
             '|---|---|---:|---|---:|---|']
    for row in heldout['inference']['comparisons']:
        low, high = row['pointwise_bootstrap_95_interval']
        text.append(f"| {row['design'].upper()} | {LABELS[row['method']]} vs {LABELS[row['baseline']]} "
                    f"| {row['mean_auc_difference']:.5f} | [{low:.5f}, {high:.5f}] "
                    f"| {row['holm_p_value']:.5f} | {'Yes' if row['superiority_supported'] else 'No'} |")
    text += ['', '## Validity, cost and runtime', '',
             '| Design | Policy | Schema | Protocol | Functional | Useful work | Estimated USD | Unknown usage batches |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
    for design in spec['designs']:
        for policy in spec['policies']:
            cells = [r for r in rows if r['design_key'] == design and r['policy_alias'] == policy]
            counts = [sum(r['validity_failures'].get(stage, 0) for r in cells)
                      for stage in ('SCHEMA', 'PROTOCOL', 'FUNCTIONAL', 'USEFUL_WORK')]
            text.append(f"| {design.upper()} | {LABELS[policy]} | " + ' | '.join(map(str, counts))
                        + f" | {sum(r['est_cost_usd'] for r in cells):.5f} "
                        + f"| {sum(r['unknown_usage_batches'] for r in cells)} |")
    timing = {key: sum(r['ledger_timing_s'][key] for r in rows)
              for key in ('wall_clock_s', 'generation_wall_clock_s')}
    text += ['', (f"Recorded configured-rate model cost is ${sum(r['est_cost_usd'] for r in rows):.5f}; "
             f"{sum(r['unknown_usage_batches'] for r in rows)} batches have unknown provider usage. "
             'Unknown usage makes accounting incomplete, not zero-cost. CPU policies have no LLM charges, '
             'not zero compute cost.'), '',
             (f"Summed trial/evaluation time is {timing['wall_clock_s']:.2f} seconds; "
             f"summed proposal-generation time is {timing['generation_wall_clock_s']:.2f} seconds. "
             'These ledger totals exclude process startup and are not a controlled speed benchmark: '
             'shared-host load and overlapping finalist validation affect elapsed time.'), '',
             '## Predeclared finalist validation', '',
             (f"{validation['matched_cases']}/16 selected seed-400 cases have matched validation, using "
             f"{len(validation['unique_replays'])} unique gate replays. Lowest-loss valid trials are selected "
             'without gate scores; ties use earliest proposal. Missing valid finalists remain missing. '
             'Duplicate cases are not independent measurements.'), '',
             (f"Successful unique replay pipeline time totals {validation['validation_wall_clock_s']:.2f} seconds "
             '(excluding synthesis, search and failed attempts). The archive records each waveform’s own '
             'timescale/span, functional checks, annotation and power components.'), '',
             '## Claim limits', '',
             ('The population ablation is AlphaEvolve-inspired, not AlphaEvolve itself. The selected '
             'controller applies bounded structural edits; it does not evolve arbitrary generator programs. '
             'DMA here uses fixed-size copies with pacing/concurrency, not the full transfer-length and '
             'backpressure space. Results do not establish random-search optimality or identify hardware '
             'size as the cause of any method ordering.'), '',
             ('GLS uses functional zero-delay cell models. Full-window mean dynamic power does not '
             'validate the eight-bin temporal power shape, and no pooled cross-design proxy correlation '
             'is claimed. These are not signoff power results.'), '']
    return '\n'.join(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--heldout', type=Path, required=True)
    parser.add_argument('--validation', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = render(json.loads(args.heldout.read_text()), json.loads(args.validation.read_text()))
    with args.out.open('x') as stream:
        stream.write(report)


if __name__ == '__main__':
    main()
