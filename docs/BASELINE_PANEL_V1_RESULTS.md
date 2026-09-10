# Stronger-baseline development results

Completed 2026-09-10. All 36 cells / 576 proposal slots passed the independent
compact-evidence audit. No models were called. This is the complete two-seed
CPU development panel, not held-out inference or an agent comparison.

## Primary endpoint first: proposal-axis AUC

Lower is better. Each arm has three targets × two seeds, sixteen slots per cell.

| Arm | Mean AUC | Solves / 6 | Valid / selected evaluations |
|---|---:|---:|---:|
| Original random | 2.5141 | 2 | 90 / 96 |
| Phase-random | 2.1659 | 3 | 93 / 96 |
| Phase-GA | 2.3707 | 2 | 91 / 96 |
| GeST adaptation, batch 2 | 2.5340 | 3 | 90 / 96 |
| GeST pool, batch 4, no screening | 2.3808 | 3 | 91 / 96 |
| Temporal ridge screening | 2.6378 | 2 | 52 / 60 |

The predeclared matched contrast is screening versus the four-candidate pool:
mean AUC difference **+0.2571**, unfavorable to screening. Seed-level differences
averaged over targets are **−0.0141** and **+0.5282**. Thus the screen is nearly
tied on one seed and worse on the other; two seeds do not establish a general
effect. Its 60 selected evaluations versus 96 is not evidence of equal-quality
speedup. Thirty-six filtered proposals have unknown validity and no measured
score. Their outcomes were not measured afterward for this study.

Phase-random has the lowest observed mean AUC and is a stronger-baseline
contender for subsequent development. This is not a statistically supported
ranking or a reason to remove competing controls. Neither GeST adaptation is
the original end-to-end framework, and ridge screening is SAGA-inspired, not
the original SAGA predictor/optimizer. This study says nothing about the
published SAGA algorithm's performance.

## Difficulty is not uniform

All arms solve the random-derived target on both seeds. On the phase-random
target, phase-random and the two GeST arms solve one seed each; the other arms
solve neither. No arm solves the scheduled-four-phase target in sixteen slots.
Its independent legal witness establishes reachability, not ease of discovery.

A separately labeled **post-hoc algebraic diagnostic** measures the best constant
vector's normalized RMS error: 0.0683 (random), 0.1202 (phase-random), and 0.3833
(scheduled-four-phase). Tolerance is 0.1. Therefore the first target does not
require nonconstant output under this error metric, while the last cannot be
matched by any constant vector. A constant vector is not itself a witnessed
legal workload. This diagnostic did not choose or modify targets.

The three pairwise target distances are 0.1467, 0.4385 and 0.4551. The bank is
balanced by its declared constructors, not by difficulty. It is not a blanket
demonstration of a harder benchmark than prior studies. Future harder-target
protocols should declare flat-vector separation and transition/dwell constraints
before construction, rather than changing this completed panel after seeing it.

## Accounting and secondary results

There are 540 selected evaluator calls: 507 valid and 33 useful-work rejections.
All invalid slots remain unscored. The other 36 proposal slots are filtered,
not invalid. Construction retained all twelve attempts (ten valid) and selected
the first qualifying witness from each constructor before policy execution.
The combined archive has 233 unique evaluation records including construction.
Cache reuse across policies/targets is expected; scheduler-dependent cache hits
are not a per-policy runtime comparison.

Mean right-censored slots to tolerance, in table order: 12.0, 11.0, 12.0,
13.1667, 11.1667 and 12.1667. Unsolved runs are retained at sixteen, never omitted.

At the per-target/seed common valid-evaluation count, mean best errors are:
random 0.1521, phase-random 0.1163, phase-GA 0.1490, GeST batch-2 0.1627,
GeST pool-4 0.1492, ridge 0.1530. This conditions on observed validity and does
not replace the primary endpoint. Common counts and all six target/seed records
are preserved in the aggregate. No p-values or confidence claims are made from
two seed units; six target/seed cells are not six independent seed replicates.

## What follows

1. Keep phase-random in the stronger baseline set; retain the matched no-screen
   control when evaluating surrogate changes. Screening has not earned a win
   claim on the primary proposal budget. Its cost/quality tradeoff remains open.
2. Confirm the selected Pro controller on the original task using the separately
   frozen fresh-seed protocol. This panel does not alter that contrast and cannot
   be combined with old Pro scores: targets and budgets differ.
3. For a new-family agent comparison, freeze a broader witnessed target bank and
   baseline configurations on separate development data. The scheduled target
   is a useful development challenge, not proof that sixteen slots are sufficient.
4. Longer horizons and more bins still require the versioned evaluator gate.
   Nothing in this eight-bin study measures watts, voltage droop or dI/dt.

## Evidence

[Protocol](BASELINE_PANEL_V1.md), [archive](../results/baseline_panel_v1/README.md),
[aggregate](../results/baseline_panel_v1/summary.json), and
[post-hoc diagnostic](../results/baseline_panel_v1/difficulty_diagnostic.json).
Auditing regenerates witnesses, target selection, candidate pools, parent
visibility, surrogate choices, CPU reference state, assembly, window arithmetic,
losses and summary metrics from compact evidence. It does not independently
resimulate waveforms. No earlier frozen study was changed.
