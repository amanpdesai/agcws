# Research results

Updated 2026-09-11. This is the authoritative findings document. All results
below concern **activity-profile synthesis** unless explicitly labeled gate
power. Lower best-so-far target-error AUC is better. Budgets, normalizations
and target banks differ across studies: do not compare their raw AUC values.

## Main result: non-flat Ibex temporal confirmation

The frozen Pro-4096 controller outperformed phase-aware random search on a
fresh, independently witnessed target bank. All **36 trajectories / 4,608
proposal slots** completed and the compact-evidence audit passed. The runner
exited successfully; this is no longer a development pilot or a running job.

| Metric | Pro-4096 | Phase-random |
|---|---:|---:|
| Mean proposal-axis AUC | **8.40173** | 27.99830 |
| Solved target/seed cases | **18/18** | 5/18 |
| Mean right-censored slots to tolerance | **16.89** | 104.06 |
| Valid proposals / 2,304 | 2,208 | 2,253 |
| Equal-valid-evaluation mean best error (secondary) | 0.03064 | 0.17098 |

Three targets × six fresh seeds (1200–1205), 128 slots per trajectory, two
shared charged initial programs, two-candidate batches. Pro uses Gemini 2.5 Pro,
4,096 thinking tokens and the previously selected fixed context/controller.
The baseline is the untuned phase-random generator qualified in development.

Primary paired AUC difference (Pro minus phase-random): **−19.59657**, about
**70.0% lower AUC**. All six seed-level differences favor Pro: −13.3091,
−21.9181, −12.9886, −20.7990, −20.4881, −28.0766. The predeclared two-sided
exact sign-flip test gives **p = 0.03125**; the seed-bootstrap 95% percentile
interval is **[−23.5461, −15.6471]**. Six seeds are the inference units, not
18 independent target/seed replicates. The p-value is at the test's resolution
floor; the interval has small-sample limitations.

### Why these targets require temporal structure

All 24 scheduled-program construction attempts passed independent checks.
Before search, the fixed selection rule chose attempts 1, 2 and 6: first valid
witnesses with constant-vector NRMSE floor >=0.20 and pairwise distance >=0.15.
Their floors are **0.48186, 0.37797 and 0.35710**, against solve tolerance 0.10.
No constant output can solve them under this metric. Witness programs were
hidden from both policies. No target was chosen using comparative outcomes.

The measurement is eight RTL bit-transition-rate bins over 200,000 cycles,
4,096 semantic body operations, fixed scale 528.45376. Releases are earliest
polling deadlines, not guaranteed idle states or phase boundaries.

### Accounting and limitations

The study made **1,134 model calls**. Known usage: 31,592,609 input tokens and
5,990,619 output/reasoning tokens, estimated **$99.39695**. Forty API failures
(31 HTTP 429, nine HTTP 504) have unknown usage and retain **$16.55360** in
reservations; total accounted liability is **$115.95055**, below the $150 cap.
This is ledger accounting, not a reconciled cloud bill.

Those failures consumed 80 Pro slots. Other Pro failures: 15 useful-work and
one schema rejection. Phase-random had 51 useful-work rejections. No failed
slot was silently retried, replaced or scored. The inherited 120-second API
deadline and disabled retries are infrastructure limitations of this frozen
study, not model reasoning failures. They were not altered mid-run.

Equal-valid comparison is conditional on observed validity; it does not erase
how previous failures affected adaptive histories. It is secondary to the
proposal-counted primary result. Censored means are not expected times to
eventual success. Shared cache warmth and serialized API calls prevent a
controlled per-policy wall-clock comparison.

**Supported:** finite-budget discovery of non-flat activity profiles on this
fresh Ibex target bank, relative to phase-random, using a frozen controller.
**Not established:** arbitrary unseen waveform families, cross-design Pro
superiority, Ibex gate-power targeting, a calibrated causal hardware model,
or a more expressive workload language. Both policies share the same language.
Targets come from one known scheduled-program distribution. This is not an
unchanged-task replication of the earlier Pro versus original-random study.

Evidence: [audited aggregate](results/nonflat_temporal_v1/summary.json),
[frozen inputs](results/nonflat_temporal_v1/manifest.json),
[target witnesses](results/nonflat_temporal_v1/targets.json),
[cost ledger summary](results/nonflat_temporal_v1/cost_summary.json).

## Earlier frozen studies: retain the negative results

| Study | Design | Random AUC | Agent AUC | Conclusion |
|---|---|---:|---:|---|
| Scalar semantic edits; 50 slots, ten seeds, five targets | AES | 2.2393 | 2.1938 | No supported advantage or equivalence against random |
| Same scalar protocol | DMA | 2.0849 | 2.6507 | No supported agent advantage against random |
| Structural temporal; 32 slots, ten seeds, two targets | AES | 3.31250 | 3.70269 | Random better; Holm p=0.03125 |
| Same structural protocol | DMA | 2.49243 | 2.73714 | No supported agent advantage against random |

The scalar study contains 550 cells / 27,500 slots and supports two corrected
DMA comparisons (agent better than mutation and scalar-edit evolution). The
scalar-edit baseline's 22.92% DMA validity limits that particular claim. The
structural study contains 160 cells / 5,120 slots. Both used frozen Flash-era
controllers and predeclared seed-level inference. Nonsignificance is not parity.

These are not overturned by the Ibex result. Architecture, controller, target
class and budget differ, so their contrast alone is not a clean model ablation.
Schema rejection does not establish that a model reasoned correctly about every
hardware constraint; adapters and a bounded grammar remove much of that burden.

Evidence: [scalar comparison](results/semantic_heldout_comparison.json),
[scalar equal-valid diagnostic](results/semantic_valid_evaluation_diagnostic.json),
[structural archive](results/structural_temporal_heldout_v1/heldout.json),
[structural equal-valid diagnostic](results/structural_valid_evaluation_diagnostic_v1.json).

## Development evidence and stronger controls

- The controlled Ibex depth study had 48 trajectories / 6,144 slots, three
  development seeds, four targets, four policies. At 128 slots Pro AUC was
  6.4399 versus original random 26.3595, with 12/12 versus 3/12 solves. The
  retrospective constant-vector check shows **nine Pro solves required
  nonconstant output**, versus zero for random/coverage and four for Flash.
  [Depth archive](results/ibex_depth_v1/README.md),
  [retrospective diagnostic](results/ibex_depth_flat_diagnostic_v1/summary.json).
- The fixed-context capability probe supported selecting Pro-4096 in
  development; it was not itself a closed-loop or held-out win.
  [Probe archive](results/ibex_capability_v1/README.md).
- The CPU baseline panel had 36 cells / 576 slots, three witnesses and two
  development seeds. Phase-random had the lowest descriptive AUC (2.1659 versus
  original random 2.5141). Ridge screening lost its matched no-screen contrast
  (2.6378 versus 2.3808); fewer selected simulations did not establish an
  equal-quality speedup. The scheduled target was witnessed but unsolved at
  sixteen slots. Two seeds do not establish a general baseline ranking.
  [Panel evidence](results/baseline_panel_v1/summary.json).
- GeST operators and the upstream SAGA predictor were inspected and qualified.
  Our phase encoding and temporal ridge screen are explicitly **adaptations**,
  not reproductions of the published end-to-end algorithms. The population
  alternative was AlphaEvolve-inspired, not an AlphaEvolve reproduction.

## Power-validation findings

1. **RTL-to-netlist annotation can be misleading.** The early AES route mapped
   only 203 of 154,059 pins and produced nearly invariant estimates. It is a
   negative methodological result, not usable power evidence. Old degenerate
   rank statistics and shared-window energy correlations are superseded.
2. **Direct GLS fixes annotation, but costs more.** Functional mapped-cell
   simulation achieved complete AES and nearly complete DMA annotation. This
   validates selected finalists; it is not the inner-loop evaluator.
3. **Full-window means hide temporal structure.** Sixteen structural finalists
   had nearly identical means within each design. Native windowed OpenSTA
   analysis of those finalists plus four references produced 180 reports:
   AES bins span 2.887–9.569 mW, DMA 20.155–21.769 mW. Maximum leaf-switching
   weighted/full discrepancy was 2.55e-08. Internal power was checked separately,
   not forced to be additive. Within four selected target/design groups,
   activity-error ordering agreed with gate-error ordering; that does not
   license a general proxy or an Ibex power claim.

Sky130 HD and Nangate45 Liberty characterization was inspected. Functional
zero-delay GLS omits timing-induced glitches; no signoff claim is made.
Evidence: [windowed measurements](results/windowed_power_v1/validation.json),
[boundary semantics](results/window_semantics_v1/verification.json),
[matched finalist replays](results/structural_temporal_finalist_validation_v1/validation.json).

## Reproduction and next work

The 2026-09-11 lossless packing pass preserves 130,015 nested evidence files in
checksummed shards across twelve studies; original paths can be restored for
review. Summaries, targets and frozen manifests stay directly readable. No
scientific evidence or earlier negative study was discarded, and Git history
was not rewritten. See [packing and recovery](results/PACKED_EVIDENCE.md).

Frozen manifests, compact trial evidence and source identities are preserved.
Historical source snapshots and protocols are separated from the maintained
pipeline; see [archive instructions](archive/README.md). No new experiment was
launched during the consolidation pass.

The [retention receipt](results/cleanup_20260911/README.md) records the scratch
cleanup: roughly 74 GiB reclaimed, preserving all cell finalists and construction
witnesses. Large logs are recoverable from local compressed objects; deleted
nonfinalist waveforms require replay. Published compact evidence was unchanged.

Remaining scientific questions: genuinely new waveform families, duration and
resolution scaling, stronger controls at matched cost, cross-design Pro
transfer, and Ibex gate-power validation. The present result supports a scoped
positive finding, not a reason to rewrite prior negative studies.

The [validation roadmap](docs/PLAN.md) orders the next work: solution inspection,
independent information/accounting audits, a post-hoc phase-GA robustness check,
then conditional fresh-family confirmation. The first inspection slice is complete
as described below; remaining checks are planned, not completed. Validity and
mechanism evidence gate stronger paper claims.

## Solution-inspection audit — 2026-09-11

Post-hoc audit, not a new comparative study. Selection was frozen at `7e43ae8d4`
before detailed program inspection, under the [protocol](docs/SOLUTION_AUDIT.md).
All 36 cells contributed first-solve, best, worst-valid and first-invalid roles
where present: 124 distinct selected records, 90 valid. Detailed inspection used
seed 1200 plus the first successful baseline seed for otherwise-unsolved target 1.
Evidence and reproduction: [audit inventory](results/solution_audit_v1/README.md).

### Consistency checks passed within their scope

All 90 valid selected programs matched the actual architectural state printed
by the archived simulator and the recorded reference. Each satisfies the frozen
4096-semantic-operation allocation and fixed 200,000-cycle observation window.
All 1,134 archived model payloads match reconstruction; all 8,160 transmitted
history rows match prior trials of the same cell. No exact witness program was
found in transmitted history, nor the checked witness/constructor metadata terms
in payloads. These are bounded checks, not proof that no leakage is possible.
Payload/reference reconstruction uses migrated implementations; independent
accounting and full simulator verification remain separate work.

The frozen constructor uses the same phase-random primitive as the baseline,
then fixes four equal-weight phases at 0/40k/80k/120k releases. Thus constructor
and agent share a phase vocabulary. Pro receives semantics and outcome feedback;
phase-random samples without using either. This is the defined comparison, but
cannot isolate semantic understanding from feedback-directed parameter fitting
or familiarity with the construction family.

### A narrower observed mechanism: polling and division

High-activity portions frequently execute the harness's active CSR/branch wait
loop; nonzero-divisor division occupies lower-activity portions. Across all
cell-best records, the mean fraction of retired instructions in polling/tail
code is 85.87% for Pro and 88.55% for phase-random. These are **instruction
fractions, not cycle or energy fractions**. They do not establish causality.

The semantic-operation floor is also weaker than application progress: the mean
fraction of operations leaving their architectural destination unchanged is
62.67% for Pro bests and 79.94% for baseline bests. This does not imply zero
switching or invalid computation. It shows why operation count alone cannot
support a claim about productive application workloads. No frozen scores or
validity decisions were changed.

Some explanations disagree with execution. Target 0's first Pro solve says its
late segment sustains the high plateau; its body finishes at cycle 104,435 and
bins 6–8 are entirely waiting by retired-instruction count. Its later best calls
an equal-release segment "parallel", although segments execute sequentially.
Successful output is not evidence that the emitted causal explanation is correct.
See [case notes](results/solution_audit_v1/case_notes.json) for failures and controls.

### Independent waveform sensitivity

Ten retained FSTs (seven detailed bests and three witnesses) were converted
offline, without simulation. An independent streaming transition counter
reproduced all original eight-bin rates exactly. It then compared each candidate
against the **measured witness waveform**, not interpolated eight-bin targets,
on 16 bins and a grid shifted by 6,250 cycles. Short end bins retain the same
physical interval; NRMSE is cycle-weighted.

| Case: target / seed / policy | Original 8 bins | 16 bins | Shifted grid |
|---|---:|---:|---:|
| 0 / 1200 / phase-random | 0.0923 | 0.1478 | 0.1397 |
| 0 / 1200 / Pro | 0.0296 | 0.0449 | 0.0471 |
| 1 / 1200 / phase-random | 0.1531 | 0.2169 | 0.1591 |
| 1 / 1200 / Pro | 0.0373 | 0.1412 | 0.0710 |
| 1 / 1201 / phase-random | 0.0342 | 0.0546 | 0.0427 |
| 2 / 1200 / phase-random | 0.0695 | 0.0772 | 0.0384 |
| 2 / 1200 / Pro | 0.0605 | 0.1305 | 0.0886 |

Two of three inspected Pro bests exceed 0.1 at finer resolution; all three remain
below 0.1 on the shifted grid. This is sensitivity evidence, **not a replacement
endpoint or new solve-rate comparison**. It supports coarse matching while
limiting sub-bin claims. First-solving Pro waveforms in these detailed cells
were not retained; compact execution records remain, and no replay was launched.

**Conclusion:** no disqualifying inconsistency was found in these checks. The
scoped eight-bin result stands, but productive computation, calibrated causal
reasoning and resolution-independent shaping are not established. Next is the
independent information/accounting audit, followed by frozen feedback/context
ablations and stronger feedback-aware controls—not a declaration that semantic
understanding has been proved. No new model calls or comparative runs occurred.

## Independent information/accounting audit — 2026-09-12

Completed under the [committed checklist](docs/ACCOUNTING_AUDIT.md), using a new
arithmetic implementation with no original/current experiment metric, cost or
payload-builder imports. All 36 cells and 4,608 proposal slots were reconstructed
from raw batches and integer activity counts. [Artifacts and reproduction](results/accounting_audit_v1/README.md).

**The published result reconciles.** Independently computed mean AUC is
8.40173035 for Pro versus 27.99830433 for phase-random; solves remain 18/18 versus
5/18. Pro-minus-random is −19.59657397, seed-bootstrap CI
[−23.54607072, −15.64707722], exact two-sided sign-flip p=0.03125. All 16/64/128
prefixes, censoring, validity counts and equal-valid secondary results agree
within 1e-10 absolute/relative tolerance. The six seeds—not eighteen target/seed
cells—remain the inference units. This verifies calculation, not new replication.

The exact endpoint convention is trapezoidal AUC on indices 1 through 128:
127 intervals, no extra slot-zero interval. Before the first valid measurement
the curve uses 1.0; valid losses are not clipped to 1.0. Six cells share an
invalid first initialization (seed 1201 across both arms and three targets),
so the convention is operative but paired equally. The prose protocol named AUC;
the implementation supplied this precise integration/invalid-prefix convention.
We disclose it rather than changing the endpoint after seeing results.

### Proposals, requests and cost

- 72 charged initialization slots across 36 cells; matching initial programs
  within each seed across arms/targets. Every cell continued to 128 after solving.
- Exactly 1,134 archived application requests: 1,094 successful responses with
  two candidates each, and 40 API failures (31 HTTP 429, nine HTTP 504), consuming
  80 slots. All successful responses report STOP, not output-token truncation.
  No short batches, discarded oversized batches or candidate replacements found.
- One generated candidate fails schema because a `divu` item lacks `dst`.
  Independent schema validation agrees with the recorded rejection. API failures
  remain a separate stage, not evidence of illegal hardware stimulus.
- 9,180 local batch files match archived bytes; request/response paths and all
  terminal cell records reconcile. No additional or unresolved **recorded** local
  requests were found. This is not a provider-side HTTP or billing trace.
- Frozen-rate estimate: **$99.39695125 known**, **$16.5536 reserved for unknown
  usage**, total **$115.95055125**. Peak reconstructed liability including the
  in-flight reservation is $116.26408875, below the $150 study cap. Thinking tokens
  are counted once. These numbers are not invoices or the remaining GCP balance.

### Cache and information access

All 2,971 unique evaluation records are accounted for: 2,943 search keys, 24
construction witnesses and four smoke evaluations. Search keys do not overlap
construction or smoke keys. Each key has exactly one recorded cache miss across
these records; actual external simulator executions are not independently counted.

| Arm | Slots with evaluation key | Recorded cache hits | Unique search keys within arm |
|---|---:|---:|---:|
| Phase-random | 2,304 | 1,540 | 768 |
| Pro | 2,223 | 44 | 2,187 |

The arm sets overlap on 12 shared initialization keys. Phase-random produces the
same 128-program sequence for each target at a given seed. Reusing measurements
is permitted and every occurrence still consumes a slot. Thus the comparison
is proposal-counted—not an equal-simulation-cost or wall-clock comparison.

All 8,160 compact-history rows and 6,588 notebook rows match earlier same-cell
records. The 66 prediction references missing from compact history are all
represented in the notebook as a row or prior prediction reference; these are
not evidence of cross-cell leakage. No checked witness metadata or witness
programs appear in history. Qualification independently selects slots 1, 2 and 6
from all 24 retained attempts using the frozen floor/distance rules.

The [source-reviewed input table](results/accounting_audit_v1/information_access.json)
clarifies the claim: Pro receives fixed semantic prose, schemas, selected history
and derived execution diagnostics. It does not directly read full RTL or invoke
shell tools. Phase-random receives RNG state and slot index, ignoring target and
feedback. That is the defined sampling control, not an ablation isolating semantics
or reasoning from feedback-directed parameter fitting. Constructor alignment
remains a distributional limitation even with a clean literal-access check.

### Corrections and limits

The first access-audit pass incorrectly expected two smoke progress messages in
the main service log. The smoke ran separately. The initial report is retained;
the corrected check derives all 2,304 expected panel progress messages from the
manifest and verifies seven smoke records separately. No study record changed.

All 82 frozen source hashes match the historical archive. Runtime source verifies
binary/image identity before execution, but the historical evaluator launches a
Docker tag and individual records lack per-replay image-digest attestations.
No drift was identified; this audit cannot prove none occurred. SDK source sets
one attempt, but local markers cannot establish provider-internal attempt counts.
Waveforms were not replayed in this slice. Existing work/polling and resolution
limitations still apply.

**Gate outcome:** no unexplained numerical or recorded information/accounting
discrepancy remains. The next slice is to freeze stronger controls and mechanism
ablations, with evaluator-equivalence checks before execution. This does not
establish semantic understanding, productive application computation, Ibex gate
power or cross-design superiority. No paid calls or new simulations were launched.
