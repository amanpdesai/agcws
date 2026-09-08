# Ibex depth v1 — interim development results

Status, 2026-09-08: the complete 64-slot prefix contains 48 cells and 3,072
proposed slots. The 128-slot panel is running. This is not completion
of the study or its primary endpoint (AUC at 128). See the frozen
[protocol](IBEX_DEPTH_V1_PROTOCOL.md) and [compact archive](../results/ibex_depth_v1/README.md).

## Complete 64-slot secondary comparison

| Arm | Mean AUC | Solves / 12 | Mean censored slots to tolerance |
|---|---:|---:|---:|
| Pro-4096 | 4.5782 | 12 | 10.50 |
| Flash-4096 | 15.7169 | 6 | 44.92 |
| Random | 15.8451 | 3 | 48.50 |
| Behavior-coverage | 19.4151 | 3 | 48.50 |

All four targets are now solved for all three Pro development seeds. Flash
solves six cells; both controls solve only the three near-flat target cells.
This is a complete secondary depth breakdown, not the still-pending primary
128-slot endpoint. Raw AUC grows with the integration horizon: do not compare
the 16-slot and 64-slot raw AUCs as if they shared an axis. The aggregate also
reports horizon-normalized AUC and all paired seed/target breakdowns.

## Complete 16-slot secondary comparison

Every arm uses all four targets and seeds 610–612, identical measurement,
two charged shared initial programs, and its own subsequent history. Lower
best-so-far error AUC is better; all invalid proposals consume slots.

| Arm | Mean AUC | Solves / 12 | Valid / 192 | Mean censored slots to tolerance |
|---|---:|---:|---:|---:|
| Pro-4096 | 2.1973 | 10 | 186 | 6.67 |
| Flash-4096 | 5.4946 | 3 | 171 | 12.75 |
| Random | 4.9947 | 3 | 160 | 12.50 |
| Behavior-coverage | 5.4105 | 3 | 180 | 12.50 |

Unsolved cells are right-censored at 16, not dropped. Pro-minus-random AUC
differences, averaged across targets within each seed, are −2.2887, −3.2414
and −2.8623. This is encouraging consistent development evidence across these
three seeds, not a significance test or held-out superiority claim.

Pro has lower mean AUC on each of the four targets. The archive includes all
target and seed breakdowns and a descriptive equal-valid-evaluation analysis;
the proposal-counted endpoint remains primary. Random and coverage reuse the
same seeded sequence across targets, whereas model requests are target-conditioned;
their cross-target unique-program counts are not measures of DSL expressiveness.

Failure counts: Pro has six useful-work rejections; Flash has twenty useful-work
and one schema rejection; random has thirty-two useful-work rejections; coverage
has twelve useful-work rejections. Counts include shared initialization failures.
No observed API failures or unknown-usage calls occur in this archived prefix.
Its 84 calls per model cost an estimated $7.4204 (Pro) and $2.0128 (Flash),
including thinking-token usage. Later running prefixes are excluded from these costs.

Public direction predictions match 637/1,328 scorable bins for Pro and
529/1,192 for Flash. These are dependent, selected scorable predictions, not
evidence of access to private reasoning or a calibrated causal model.

## Scope and verification

This study measures temporal RTL activity on programmable Ibex, not gate-power
superiority or greater language expressiveness. All arms share the same program
language. Prior frozen negative studies remain unchanged. No controller changes
or target selection follow from this interim ranking.

Compact auditing reconstructs CPU state from recorded console evidence, checks
source and binary provenance, regenerates proposals and payloads, verifies usage
and charged slots, and independently integrates prefix curves and censoring.
It does not rerun simulation or independently reproduce waveforms. The archive
explicitly reports `complete_study: false`. The test suite passes 514 tests
with three existing Ray/fork warnings; the active study and analysis lint cleanly.
