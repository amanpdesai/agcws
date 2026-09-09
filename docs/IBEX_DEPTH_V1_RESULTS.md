# Ibex depth v1 — complete development results

Completed 2026-09-09: 48 trajectories, 6,144 proposed slots, and all declared
16/64/128 prefixes. The producer exited successfully. This completes the
development study, not a held-out claim or the entire project. See the frozen
[protocol](IBEX_DEPTH_V1_PROTOCOL.md) and [compact archive](../results/ibex_depth_v1/README.md).

## Primary endpoint: AUC at 128 slots

| Arm | Mean AUC | Solves / 12 | Valid / 1,536 | Mean censored slots to tolerance |
|---|---:|---:|---:|---:|
| Pro-4096 | 6.4399 | 12 | 1,507 | 10.50 |
| Flash-4096 | 24.6608 | 7 | 1,368 | 73.58 |
| Random | 26.3595 | 3 | 1,420 | 96.50 |
| Behavior-coverage | 35.0842 | 3 | 1,453 | 96.50 |

Pro's mean AUC is 75.6% lower than random's on this development panel.
Its mean AUC by seed is 5.6749, 6.3831, 7.2617, versus random's
25.0457, 27.8288, 26.2041. All Pro target/seed cells reach tolerance by
64 slots; continuing to 128 follows the frozen full-curve protocol rather than
stopping selectively after a favorable result. Random and coverage solve only
the three near-flat cells. Flash solves seven cells but remains much closer to
random in mean AUC than to Pro.

This is the first completed on-policy depth comparison here with a large,
consistent Pro development advantage over both controls. It supports pursuing
fresh held-out confirmation, not announcing general model superiority. Both
models receive the same 4,096-token thinking allowance, context, tools and
proposal budget; actual tokens and latency differ. The task is temporal activity
matching on one programmable CPU, not a cross-design power optimization result.

### Accounting and reliability

There were 756 attempted calls per model. Known estimated cost is $74.6654
for Pro and $19.8660 for Flash, or $94.5315 combined. Five Pro HTTP 429
responses have unknown usage; this is not an exact total bill. They consume ten
API-failure slots, with no retries, substituted policy or free proposals. All
1,507 successful provider responses report STOP; no unresolved request remains.

Pro rejection counts are 14 useful-work, 5 schema and 10 API slots. Flash has
115 useful-work and 53 schema rejections. Random has 116 useful-work rejections;
coverage has 83. No failure receives a loss. These counts include initialization.
The aggregate preserves the equal-valid secondary analysis, all seed/target
breakdowns, prediction diagnostics and costs; no cells are dropped.

At the per-cell common valid-evaluation count, the mean best-error secondary
metric is 0.0541 for Pro, 0.1899 for Flash, 0.2098 for random and 0.2783 for
coverage. This conditions on observed validity and is descriptive; it does not
replace proposal-counted AUC. It indicates the Pro gap is not solely a result
of the validity-rate difference. Seed-level Pro-minus-random primary AUC
differences are −19.3708, −21.4458 and −18.9423.

Public direction predictions match 5,857/11,848 scorable bins for Pro and
4,951/10,744 for Flash. A strong search outcome does not itself establish
well-calibrated causal explanations; these dependent prediction checks remain
a separate diagnostic, with no private reasoning trace claimed.

A 2026-09-09 re-analysis of the archived scorable direction labels finds
Pro counts (down, up, neutral) = (3,717, 4,711, 3,420), and Flash counts =
(3,995, 4,335, 2,414). Their pooled majority-label reference accuracies are
39.8% and 40.3%, versus model accuracies 49.4% and 46.1%. These are
three-class predictions, not binary coin flips; describing 49.4% as "chance"
is incorrect. This pooled diagnostic is not a calibrated causal-model test
or a significance calculation; references and bins are dependent.

## Complete 64-slot secondary comparison

| Arm | Mean AUC | Solves / 12 | Mean censored slots to tolerance |
|---|---:|---:|---:|
| Pro-4096 | 4.5782 | 12 | 10.50 |
| Flash-4096 | 15.7169 | 6 | 44.92 |
| Random | 15.8451 | 3 | 48.50 |
| Behavior-coverage | 19.4151 | 3 | 48.50 |

All four targets are now solved for all three Pro development seeds. Flash
solves six cells; both controls solve only the three near-flat target cells.
This is a complete secondary depth breakdown. Raw AUC grows with the integration horizon: do not compare
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
explicitly reports `complete_study: true`. The test suite passes 514 tests
with three existing Ray/fork warnings; the active study and analysis lint cleanly.
The complete compact audit passes for 48 cells, 6,144 slots and 61,081 files.
