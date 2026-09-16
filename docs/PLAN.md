# Plan

## Active slice — clean three-arm baseline restart (2026-09-16)

The user superseded the old panel and stopped Ibex. Preserve historical evidence,
reclaim redundant traces losslessly, and enable automatic retention. Implement
`phase-model` alongside unchanged phase-random and phase-GA; validate only on
development targets before freezing a clean full-panel source state. No old
cells/caches are reused. See [BASELINES_MODEL_V1.md](BASELINES_MODEL_V1.md).
Do not launch a full or paid matrix in this slice. Earlier progress entries
below are historical and do not override this decision.

Implementation and smoke are complete: 15 CPU cells / 180 proposals across all
five designs, archived and restored exactly. Full three-arm manifests are
prepared for 1,350 fresh cells at runtime commit `a025d4f9f`; task contracts,
images and simulator identities match the stopped panel. No full cells or API
calls have started. Bulk historical waveform verification/retirement remains
in progress; do not describe that cleanup as complete until its receipt exists.

## Previous goal — common bit activity and CPU requalification

Update: all ninety requested profiles now have valid bit-metric witnesses.
Mesh's separate local-refinement supplement passed its 2,048-slot trajectory
audit and archive restoration audit. Preserve the original 14/18 bank.
Next: refresh full Flash/baseline configurations against the new banks, verify
matched task identities and witness exclusion, then request launch approval.
No further witness search or paid study is currently running.

User approved the next slice after the audit. Implement and test
[BIT_ACTIVITY_V1.md](BIT_ACTIVITY_V1.md), replay the fixed calibration/witness
programs, regenerate analytic targets from the new metric, and retain every
failed qualification. No LLM calls or full panel. New source fingerprints must
not be bridged as measurement-equivalent to the old identifier-event metric.
The old banks stay intact and are not current-runtime launch inputs.

The first 410 fixed-program replays completed with 401 valid measurements and
nine retained useful-work failures. Independent recounts match all eight
preselected schedule traces. A separate Ibex marker-offset regression exposed
a boundary-assignment defect; [alignment v2](BIT_ACTIVITY_ALIGNMENT_V2.md)
preserves the first round and declares the correction before fresh replay.
Corrected five-design replays are in progress. Next: freeze new-unit analytic
requests, exhaust only the declared CPU witness searches where necessary, and
audit every attempt before admitting any bank. Full-study readiness is not
restored merely by finishing a replay.

## Current stopping point — task audit finished, full-study gate on hold

Operational readiness passed, but the user requested a separate critical task
audit before any full baseline or LLM panel. The audit reproduces calibration,
witnesses and baseline arithmetic, but finds representation-sensitive activity
counting, especially for mesh. Launch remains on hold pending a versioned
measurement-contract decision and user approval. See
[TASK_QUALITY_AUDIT.md](TASK_QUALITY_AUDIT.md).
Existing banks and measurements are preserved; any measurement correction needs
a new version, not an in-place change to a frozen comparison.

## Previous stopping point — operational readiness

All five banks have eighteen admitted requests; all ninety have actual generated
measurement feedback, including the explicitly separate DMA late-delivery
diagnostic. The original v4 and v5 strict failures remain recorded. See
[RESULTS.md](../RESULTS.md) and the
[readiness receipt](../results/benchmark_readiness_v1/full-flash-readiness-v1.json).
Full-study configurations are prepared and frozen, not executed. Next action
is now the recommended common bit-transition contract and requalification,
followed by the user's launch/spending approval. No corrective run is authorized
by this audit completion alone.
Read the cost caps and claim limits in [FULL_FLASH_V1.md](FULL_FLASH_V1.md).

The intervention entries below describe the path to this stopping point.

## Current intervention — exact arithmetic feedback v5

The archived v4 failures motivate explicit signed budget arithmetic in visible
AES/DMA history, with no candidate repair, new oracle access or changed gates.
See [frozen intervention](BUDGET_FEEDBACK_V5.md). This changes runtime source
identity; current-source calibration/witness replays have passed for all five
designs, with versioned v5 banks and compact evidence. Exact context replay of
126 calls each shows mesh/Ibex/RedMulE payloads, schemas and parsing unchanged;
only AES/DMA require new-context feedback checks. All v4 manifests and results
remain unchanged.
The user approved audited operational readiness with retained failures and
liability. Subsequent [failure diagnosis](SMOKE_FAILURE_DIAGNOSIS.md) found that
our 120-second client deadline is forwarded to Vertex and all four 504s occur
at that boundary. The transport policy now records a ten-minute deadline and
one SDK attempt in model settings. All five static transport-only bridges
preserve measurement implementation and runtime identities; these are not new
simulation replays. AES/DMA arithmetic compliance still needs prospective
verification under the [v5 follow-up](BANK_SMOKE_V5.md). No full study has launched.

The [prospective full Flash protocol](FULL_FLASH_V1.md) fixes ten fresh search
seeds, nine confirmation requests per design (eight substantive plus control),
three matched arms, 128-slot ceiling and batch-end early stopping. The target
vectors themselves have been seen during engineering; do not call this unseen
task generalization. All five configs may be prepared now, but launch remains
unauthorized until feedback readiness and the user's spending approval.

## Current action — 2026-09-14, context v4

All five current-runtime banks are admitted: eight nonflat requests plus a
control in each split. RedMulE's expert bin constructor qualified 18/18 without
changing the longer-window requests or gates; this is not an agent result.
Bounded history is merged, with exact calibration/witness replay evidence.

The frozen [v4 smoke](BANK_SMOKE_V4.md) finished across all five designs,
all eighteen requests, Flash/random/GA, seed 8502 and sixteen slots. It passes
88/90 measured-feedback checks and 85/90 strict checks. All failures and
unknown-call liability remain recorded; do not seek a favorable-seed retry.

Next: address the measured AES/DMA exact-budget feedback limitations with a
separately declared corrective interface/procedure. Resolve the explicit
approval question about operational readiness with recorded server failures;
do not silently weaken the strict v4 gate. Then prepare fresh-seed full-study
configurations and the readiness receipt. The full 128-slot Flash study still
requires user approval.

The dated entries below are historical milestones, not current launch status.

## Ibex all-target feedback gate passed — 2026-09-14

The current-runtime Ibex bank is admitted and its single frozen v3 smoke
passes 18/18 requests: actual generated measured feedback, known Flash usage,
shared initialization and charged-slot checks. Archive:
`results/ibex/bank-smoke-v3/`. The full five-design study remains unlaunched;
RedMulE qualification and the other documented readiness gaps remain open.

## Full-budget context gate — 2026-09-14

An offline repeated-valid-workload stress check exposes a launch risk in
AES/DMA/mesh: unbounded history can exceed the request guard before 64 slots.
See `results/benchmark_readiness_v1/context_capacity.json`. This is synthetic
capacity evidence, not an observed model failure or a policy result.

A bounded-history correction is being tested on isolated branch
`readiness-context-v4`; do not merge into the source mounted by live RedMulE
qualification or Ibex smoke jobs. Integration, runtime provenance and fresh
bounded smoke checks must precede the full 128-slot study. Do not weaken the
guard, silently truncate payloads or assume successful short smokes prove
full-budget capacity.

## Authorized RedMulE window experiment — 2026-09-14

Test the independently versioned 262,144-cycle domain under
`REDMULE_LONG_WINDOW_V1.md`, with fresh 64-proposal calibration and unchanged
qualification gates. Keep the 65,536-cycle bank and every failed attempt.
Do not launch the full paid study. The runtime change requires explicit
provenance bridges before any other-design bank is promoted as current.

The sixteen-slot AES/DMA/mesh feedback smokes have finished, each with 17/18
strict readiness; all failures and unknown-call liability are retained in
per-design archives. The Ibex modeled witness panel qualifies all eighteen
requests; its full 64-case calibration waveform comparison matches after
excluding only VCD header date metadata. These are progress, not yet a
five-design launch gate pass.

## Five-design readiness checkpoint — 2026-09-14

DMA now qualifies all eighteen requests under its corrected 9,216-cycle window.
AES and mesh passed exact current-runtime replay of all 64 calibration programs
and eighteen witnesses each. Their original banks remain intact; the new bank
versions carry explicit replay lineage.

Bounded six-slot Flash/random/GA smokes are complete across these three designs,
all eighteen requests each. Generated-feedback readiness passes AES 12/18,
mesh 17/18, DMA 13/18; API calls succeed with known usage, but first generated
batches sometimes contain no valid workloads. Exact work/idle arithmetic is the
main AES/DMA failure. Preserve this evidence before any new smoke protocol;
do not repair candidates, relax gates, or repeat until a favorable draw appears.

RedMulE's 354-slot fixed operand sweep added no qualified targets. Ibex's 88
fixed-operation measurements all pass functional checks and identify division
operands as low-activity building blocks; no new target witness is claimed.

Next work, in order:

1. Freeze a target-guided Ibex construction using the measured operation profiles;
   retain every attempt and the original requested vectors and tolerance.
2. Diagnose RedMulE timing/quantization limits before another broad search. Its
   remaining misses are not yet proof of infeasibility or grounds to drop shapes.
3. Separate Flash contract-compliance limitations from transport correctness.
   Declare any longer feedback smoke or interface change before execution,
   preserving failed v2 smokes. Do not substitute Pro for the requested Flash test.
4. Finish missing qualifications and all-target feedback checks, archive/replay
   audits, then freeze full-study settings and seek launch approval. The full
   five-design study is still not ready and has not launched.

Updated 2026-09-13. Findings and completion status live only in
[RESULTS.md](../RESULTS.md); compact evidence lives in `results/`.

## Where we stand

The consolidation milestone is complete at `72a8bc663`: one maintained study
pipeline, a verified historical source archive, published compact evidence and
documented scratch retention. Verification is recorded in
[archive/verification.json](../archive/verification.json).

The scientific evidence supports a scoped Pro-versus-phase-random finding on
one Ibex target-construction family. It does not yet establish the mechanism,
arbitrary temporal-profile
generalization or Ibex gate-power accuracy. Earlier frozen negative studies
remain part of the paper. Differences in design, model, budget and task prevent
attributing their contrast to interface expressiveness alone.

The untuned 128-slot phase-GA extension is now complete; it did not close the
observed Pro gap, with the frozen inference limits recorded in RESULTS.md.

## Active milestone — five-design benchmark readiness

The next engineering gate is the [runtime refresh](RUNTIME_REFRESH_V2.md):
verify the corrected DMA window, refresh its calibration, certify existing
AES/mesh evidence against the new source identity, and complete Ibex/RedMulE
witness qualification. Provider-grammar integration must be exercised through
real bounded feedback smokes, not counted as complete from mocked tests.

The September 13 user decision prioritizes five fully functioning designs over
leaving cross-design work as a late optional port. Keep Ibex/AES/DMA and evaluate
two additions before agent outcomes. Selection evidence, candidates and mandatory
functional/measurement/target/smoke gates are in [BENCHMARK_SUITE.md](BENCHMARK_SUITE.md).
This authorizes bring-up, CPU target qualification and bounded cheap-model smoke
tests, not a new paid comparative matrix or a five-design performance claim.
Independent target qualification remains necessary; existing frozen studies are
not changed. The earlier conditional ordering below is superseded where it would
defer suite readiness until after another Ibex-only confirmation.

## Research priorities — September 12 amendment

Scalar is a completed finding, not a new experiment priority. Preserve its
frozen comparisons: random was competitive or best among the tested policies;
this does not prove near-optimality. The AES calibration transition from 0.80
solved at tolerance 0.05 to 0.20 at 0.02 describes that calibration, not universal
task difficulty. Temporal targeting is the next discriminating regime.

The implemented task is goal-conditioned search through a bounded interface.
Adapters and checks reduce the low-level legality burden; they do not guarantee
that every proposal is legal. Thus the original long-sequence semantic hypothesis
was only partially exercised. A win alone cannot establish semantic understanding.

Cross-design performance claims now require a second completed temporal design
study. Until then, narrow the abstract to the Ibex result and distinguish it from
three-interface harness reuse. Preserve earlier negative studies unchanged.

### First slice: existing-evidence analysis and stronger-control readiness

**Complete 2026-09-12, within the declared offline scope.** Reproduction and
limits are in [the evidence bundle](../results/evidence_extension_v1/README.md).
F1–F3 are computed; F4 reconciles local liability but external balance/access
remain unverified. Early C4 provides 15 readable examples with missing shape
categories explicit. The untuned [phase-GA protocol](PHASE_GA_ROBUSTNESS_V1.md)
and offline historical/current checks are recorded. The next execution slice
was runtime identity plus matched live replay, then V2 only if that gate passes.
On September 12 all seven live replays passed and V2 started under its recorded
execution manifest. V2 completed and passed its accounting audit on September 13:
18 cells / 2,304 slots, no provider calls. See RESULTS.md for paired inference
and limits. The preceding planning/analysis slice launched no runs.

No paid calls or new simulations in this slice. Produce a compact, reproducible
analysis bundle linked from RESULTS.md, plus an execution-ready robustness
protocol. Do not conflate writing that protocol with running it.

| Item | Work and acceptance condition |
|---|---|
| F1 | Recompute paired 16/32/64/128-slot prefixes from existing 128-slot curves. Preserve the frozen AUC convention, censor at each prefix, and report AUC and solve rates together. Label post-hoc descriptive budget sensitivity; do not select a favorable headline cutoff. |
| F2 | Add per-run cost and total accounted cost divided by solved cells, including spending on unsolved cells. Zero solves means undefined cost per solve, not zero. Separate known estimates, unknown-call liability and unpriced CPU/runtime cost; no invoice claim. |
| F3 | Define and compute ten-bin coverage using each corpus's own frozen scalar envelope, valid-work gate and measurement units. Record bin/tolerance rules, out-of-envelope values and denominator. Do not substitute temporal-bin values for whole-workload scalar coverage or pool incompatible calibrations. Report capability coverage, not a retrospective policy contest. |
| F4 | Reuse the completed local liability reconciliation; identify the remaining external checks for actual available credits, billing and organizer access. Never infer the balance from an old $300 allocation or mark unknown usage as free. |
| Control readiness | Inspect and freeze untuned phase-GA settings, matched initialization, targets, seeds, 128-slot accounting and feedback. Check offline evaluator fixtures and specify any live equivalence check required before execution. Scope the simple division/polling scheduler and feedback/context ablations separately; do not silently add arms. |

Exit: reproducible analyses, explicit missing-data/external-account limitations,
and a reviewed protocol with execution prerequisites. This is not evidence that
new controls have run. If equivalence requires simulation, leave that gate open
for the next authorized execution slice.

### Validity sequence after the first slice

1. **V1 — complete, bounded:** solution inspection and independent accounting.
   Missing first-solve traces remain a documented limit, not an indefinitely
   open audit. New replay would require a separate decision.
2. **V2 — execute stronger control:** untuned phase-GA at 128 slots on the existing
   confirmation panel, after evaluator equivalence. Report as post-hoc robustness.
3. **V3 — qualify independent targets:** freeze a different generation and witness
   search procedure; retain all attempts and failures. Include a difficulty
   gradient and at least one below-tolerance constant-floor control **with a
   legal near-flat witness**, not merely a mathematically fitting constant vector.
4. **V4 — fresh confirmation:** freeze qualified targets, controls, controller,
   inference and fresh seeds before comparison. Keep the eight-bin horizon fixed.

A gate passes when evidence is trustworthy and analyzable, not when Pro wins.
If a control explains the advantage, report that and revise the next question.

### Conditional extensions and deliverable extraction

- **C1/C2:** port minimum shared contracts to DMA first, verify offline fixtures
  and measurement equivalence, then run a separately frozen second-design temporal
  comparison. A model-string substitution is not a backend port.
- **C3:** either explicitly descope compositional claims or freeze and run an AES
  compositional study. Region support is not an experimental result; a CPU
  multiplier/divider example must not imply a demonstrated AES capability.
- **C4, early and independent:** extract a directly readable characterization
  suite from existing evidence alongside the free analyses. Use deterministic
  selection rules for low/mid/high/burst/ramp representatives where supported,
  with measured profiles, validity, provenance and source links. Mark missing
  categories rather than inventing examples or measurements. Activity-only
  records are not power-validated workloads. Extraction need not wait for C1–C3.

Order: first-slice analyses/control readiness and early C4 → V2 → V3 → V4 →
C1 → C2 → conditional C3. Preserve methods notes throughout. Longer horizons,
16-bin targets and additional designs remain separate deferred axes, selected
for measurable difficulty spread rather than presumed expressiveness.

## Next milestone: try to falsify the result

The objective is not to make the agent win more. Seek evaluator errors,
information asymmetries and comparison-design weaknesses that could explain
the observed advantage. A large effect motivates scrutiny, but is not itself
evidence of a confound. Audit consistency and scientific validity separately.

The upcoming extensions are planned, not executed or pre-registered by this document.
Freeze the inspection selection before opening solutions; freeze any extension
protocol before evaluation. Do not launch jobs merely by following a status
page. New measurements and paid calls require an explicit execution decision.

| Order | Work | Status | Exit condition |
|---|---|---|---|
| 1 | Inspect solutions and measurement behavior | DONE — bounded offline audit | Findings and remaining limits in RESULTS.md; no new runs |
| 2 | Audit information access and accounting independently | DONE — bounded offline audit | Independent metrics/costs reconcile; causal and provider-side limits remain |
| 3 | Phase-GA robustness extension at 128 slots | DONE — post-hoc robustness | All 18 cells audited; compact evidence and frozen paired analysis in RESULTS.md |
| 4 | Qualify a more diverse target bank | PLANNED — NOT LAUNCHED | Freeze construction/search rules and retain every attempt |
| 5 | Fresh broader confirmation | CONDITIONAL | Qualified targets, frozen controls and sufficient analysis time |
| Gate | Paper claims | WAITING ON VALIDITY | Audit validity and test competing mechanisms before finalizing claims |

### 1. Solution inspection: cheapest falsification first

Before inspecting programs, record a deterministic selection rule. Cover all
three targets, first-solving and best programs, and representative baseline
solutions and failures. Select by declared seed/slot rules, not by whether the
program looks convincing. Explain ties and cases with no solve. A few examples
can find a failure mode; their absence cannot prove the entire panel is sound.

For each selected trajectory, inspect the exact submitted program alongside:

- Its phase releases, allocated operations, operands, dependencies and memory effects.
- Executed retirement and phase timing, not just the intended schedule.
- Useful-work accounting, including repetitive or ineffective operations that
  pass the counter without supporting a stronger notion of useful computation.
- Requested and achieved activity bins, observation boundaries, reset/wait/tail
  behavior and whether execution finishes in the declared window.
- First-solve versus later-best behavior, so attractive final programs do not
  hide how the tolerance was first reached.

Use retained traces for finer-resolution and shifted-bin diagnostics, with
explicit boundary handling and the same physical observation interval where
possible. These are sensitivity checks, not replacements for the frozen
eight-bin endpoint. Eight-bin matching does not promise sub-bin matching.
Record missing traces and any replay need: cleanup retained best-candidate and
witness waveforms, not necessarily every first-solving waveform. Compressed
execution logs and compact records remain available; do not silently replay.

Classify findings as simulator/evaluator error, legal exploitation of an
underspecified objective, or plausible workload behavior. A legal but vacuous
useful-work solution may narrow the claim even if functional checks pass.
If a defect could invalidate results, pause stronger comparisons and identify
the affected cases before correcting or withdrawing claims.

### 2. Information access and independent accounting

Completed under [ACCOUNTING_AUDIT.md](ACCOUNTING_AUDIT.md); evidence is indexed in
[the audit archive](../results/accounting_audit_v1/README.md). Independent raw-record
reconstruction agrees with published metrics and local request accounting.
This does not establish provider billing, runtime identity on every replay or
semantic understanding. The first implementation discrepancy was an audit-log
expectation, documented and corrected without changing study records.

Next freeze mechanism controls before running them: feedback-free versus correct
feedback, schema-only versus semantic context, phase-GA at matched budget, and a
simple division/polling scheduler. Keep model, targets, work and budget fixed when
isolating each intervention. These controls are planned, not authorized here.

The first slice found active polling and repeated state-preserving operations
within the legal task. Distinguish operation-count compliance from application
progress. Any stronger useful-work requirement needs a new protocol; do not
retroactively disqualify the frozen results. Finer-bin matching likewise needs
fresh targets and a declared endpoint, not reclassification of eight-bin solves.

Inspect the frozen, actually sent payloads and original sources, not only the
new runner. Build an information-access comparison for Pro and the controls:
target vectors/scales, schema, hardware semantics, history, diagnostics and
initial programs. Check witness contents, constructor settings, hidden target
metadata, cross-cell history and witness/cache reuse paths. A common cache is
not proof of leakage; verify what information could reach the policy.

Separate three hypotheses:

1. **Actual leakage:** hidden witness programs, constructor parameters or other
   cells' results reached the controller contrary to the protocol.
2. **Unequal information:** target-specific hints or feedback were unavailable
   to the comparison policy despite the claimed fairness contract.
3. **Distribution alignment:** a policy recognizes structure common to the
   constructor's target family. This limits generalization without necessarily
   invalidating the scoped comparison.

Compare prompt/adapter vocabulary with constructor parameters, then trace the
meaning and visibility of overlaps. Grepping is a lead, not a verdict. Shared
phase vocabulary is expected when every policy uses the same phase language;
target-specific template disclosure is a different issue. Out-of-family
testing is needed for a broad claim regardless of a clean literal-leakage audit.

Reconstruct the primary endpoint from raw records using an independently
reviewed calculation, not merely the original summary helper. Reconcile every
requested slot, initialization, malformed/short batch, API failure, duplicate,
cache hit, selected/filtered proposal and valid measurement. Check AUC indexing
and invalid-prefix handling, normalization, right-censoring, seed pairing,
cost/unknown-usage reservations and the exclusion of witness qualification from
search histories. Compare the reconstruction to published aggregates. Preserve
all discrepancies; do not fix records to obtain agreement.

### 3. Stronger-control robustness check

Run phase-GA at 128 proposed slots on the existing confirmation targets and
seeds, with matched initialization, measurement, feedback and accounting.
Inspect the qualified implementation and freeze its exact settings first.
Do not tune it on these now-observed targets. If tuning is necessary, use a
separate development bank and declare the tuning budget.

This is a **post-hoc robustness extension**, not an amendment to the original
held-out confirmation. Keep its outputs separate. Verify evaluator equivalence
before combining new baseline measurements with historical Pro records; the
new runner's unit tests alone do not establish measurement equivalence.
If phase-GA closes the gap, narrow the advantage claim. If it does not, report
the tested control and uncertainty rather than declaring all classical search
defeated. CPU-only means no model-token cost, not zero runtime or compute cost.

### 4. Target diversity before larger hardware

Prioritize independent targets over adding more seeds to the same three targets.
Vary uneven steps, separated bursts, ramps, transition count, dwell lengths and
contrast. Include achieved targets from different program families and
classical-search-generated witnesses. A different constructor is a test of
distribution sensitivity, not automatic proof that all constructor effects are
eliminated. Larger hardware is not the default next step.

For analytic requests, freeze before qualification:

- Family definitions, sampling distribution, seeds and number of attempts.
- Horizon, bin grid, scale, useful-work gate, non-flatness and distance rules.
- Witness-search policies, per-attempt budget, matching tolerance and stopping rules.
- Acceptance/selection order and treatment of failures and duplicate witnesses.

Retain **every** request and qualification attempt, including failures. Distinguish
the analytic request, the achieved witness profile and their distance. Decide
in advance which is the scored target. Failure to find a witness is not proof
of infeasibility; do not quietly substitute an easier waveform. Report the
acceptance rate and resulting selection bias. Qualification must not use Pro's
comparative success to select targets. Witness programs remain hidden from
search unless a separately labeled, equally available reference-edit study is
explicitly declared.

Start with the existing horizon and eight bins to isolate target-family change.
Longer horizons and 16-bin resolution are separate scaling axes requiring their
own feasibility and measurement checks, not simultaneous changes to this panel.

### 5. Fresh confirmation and paper decision

Freeze the controller, qualified target bank, baseline settings, endpoint,
inference and failure handling; declare fresh seeds before comparative runs.
Scope the claim to the qualified distribution. Do not merge incompatible study
regimes or rewrite earlier outcomes. Cross-design Pro addresses generalization;
Ibex gate-power validation addresses the power claim. They are distinct,
conditional extensions, not substitutes for validity checks.

Validity and mechanism evidence gate the paper. The user has explicitly chosen
thorough investigation over rushing the manuscript. Preserve evidence and
methods notes as work proceeds, but do not use writing pressure as a reason to
stop testing alternative explanations. A policy win is not a demonstration
that semantic understanding caused it.

Size extensions from measured runtimes, qualification yield and available
analysis/writing time, not assumed one-day or week-long estimates. Proceed with
the broader confirmation only after steps 1–4 pass their gates and there is time
to finish analysis, not merely launch jobs. If a broader claim remains unsupported,
retain the narrower scope rather than treating a deadline as validation.

The completed first audit follows the frozen
[inspection protocol](SOLUTION_AUDIT.md); it is not the next implementation task.

## Cross-design and corpus extension — planning, not a launch authorization

The user prioritizes thorough validity and mechanism evidence before the paper.
Do not inherit a six-day deadline or a $300 remaining-balance assumption from
secondary feedback. Additional funding was reported; reconcile actual usage,
unknown-call liability and available credits before sizing a paid study. Treat
any organizer-provided future account window as unconfirmed until access and
limits are checked. Do not depend on it to finish a promised experiment.

### What the current contrast does and does not establish

Adapters span three interface types, and shared schemas/context templates
demonstrate infrastructure reuse. Completed positive Pro evidence is Ibex;
earlier Flash negatives are AES/DMA in different protocols. Model, design,
budget and task differ, so their contrast does not identify a cause.

Pro on DMA, then AES, is the lowest-bring-up cross-design direction. However,
those adapters and historical flows are not already maintained backends of the
new orchestration: `docs/PIPELINE.md` currently lists Ibex only. First inventory
and port the minimum shared contracts, preserve archived implementations, and
verify semantic equivalence with offline fixtures before scheduling real runs.
Do not claim that this is merely changing a model string and executing.

A Pro null on a bounded DSL would not isolate expressiveness. AES/DMA already
produced distinct temporal shapes, while Ibex also uses a bounded phase grammar,
not arbitrary executable programs. Architecture size and interface names are
not measurements of expressiveness. Even a CPU configuration change can alter
ISA legality, divider latency, synthesis and the empirical envelope; requalify
targets and references instead of calling it free transfer.

### Ordered extension slices

| Order | Slice | Gate before execution |
|---|---|---|
| 1 | Independent information/accounting audit | Reconcile all raw calls, proposals, retries, caches, initials and costs; resolve any material discrepancy |
| 2 | Stronger matched-budget and mechanism controls | Freeze phase-GA and division/polling scheduler settings; define feedback/context ablations without tuning on the confirmation panel |
| 3 | DMA/AES backend readiness | Shared runner contracts, complete schema, actual useful-work semantics, matched observation windows, offline golden cases and recorded tool/model identities |
| 4 | Fresh cross-design protocol | Matched within-design Flash/Pro/control comparisons, witnessed non-flat targets, fresh seeds and a measured budget projection |
| 5 | Additional designs, one at a time | Predeclared selection rubric and legal, calibrated witnessed targets before admitting a design |

Order 1 and the existing-evidence/phase-GA readiness slice are complete within
their offline scope. V2 completed with audited compact evidence; phase-GA did not
close the observed Pro gap (see inference limits in RESULTS.md). Next: V3 target
qualification, with independent construction and all attempts retained. Other mechanism arms remain separately
scoped, not frozen implementations. This is not a paid cross-design matrix.
Prepare the cross-design protocol after readiness and accounting establish what
can actually be held fixed. Record proposed settings now, but do not label an
unfinished configuration or unqualified target bank "frozen".

### Isolating context, feedback and expressiveness

Within each design hold model settings, budget, target bank, seeds, initial
programs, validity gates and evaluator fixed when changing one factor. Compare
Pro and Flash under the same new protocol; do not use old Flash numbers as the
control. Include phase-aware random and feedback-aware classical search where
applicable. Report proposal-counted AUC first, right-censored solve rates,
equal-valid-evaluation diagnostics and actual cost. Match feedback frequency
or explicitly label it as a second factor.

For a language-expressiveness claim, specify operational measures in advance:
number of independently controllable phases, duration/release resolution,
instruction/data-mix choices, legal sequencing depth and achieved profile-family
coverage. Consider nested restricted/full grammars **within a design**, with
identical grammar access for every policy. Separate witness feasibility from
policy success; a target unreachable in a restricted grammar is a representation
limit, not a failure of its search algorithm. Avoid selecting grammars or targets
because they produce a desired model ordering.

Correct-feedback versus feedback-free and semantics versus schema-only arms
test whether those inputs help; they do not reveal private reasoning or prove
human-like understanding. Preserve predictions and executed trajectories for
mechanistic checks. The observed polling/division alternative must get a fair
classical control before attributing an advantage to deep RTL understanding.

### Conditional corpus of up to six designs

Six is an exploration ceiling, not a completion requirement. First test Pro on
the existing designs; then admit additional designs using a declared rubric,
including cases expected to favor classical search. Candidate categories from
the discussion are a temporally controlled NoC, a configurable dataflow block,
and a FIFO/interconnect control. These are not selected dependencies: check
upstream availability, license, synthesizability, simulation and work semantics
before choosing a repository or promising an adapter.

Seek independent variation in temporal control and sequencing depth, not three
nominally "expressive" labels versus three "bounded" labels. Record every attempted
bring-up and why it was admitted or cut. A proposed 1.5-day readiness timebox is
a planning limit, not a runtime timeout or evidence of infeasibility. Missing
the gate should reduce the corpus, not invite weakened validity or easier
undisclosed targets. No larger corpus supersedes the original frozen studies.

### CHIA deliverable remains a separate gate

Preserve reusable measurement nodes and verify their actual CHIA execution path
before submission. Import counts alone do not establish dead code or successful
integration. A tested wrapper is not an upstreamed contribution; do not claim
an upstream PR or acceptance until it exists. Backend ports should reuse shared
contracts rather than duplicate the historical Ibex runner.
