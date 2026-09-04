# Results status

This file records the strongest verified results currently present in the
repository. It is not the final paper result: the declared 10-seed,
multi-design factorial study has not yet been completed.

## Verified infrastructure

### Oracle responsiveness finding

A clean 20-workload AES calibration after widening the generator produced
20/20 valid workloads and an RTL activity range of 22.25--130.29 transitions
per clock edge (486% relative spread). OpenSTA still annotated only 203 of
154,059 pins (0.132%), yielding a total-power range of only 0.050% of its
minimum. This isolates the current bottleneck to RTL-waveform-to-netlist
annotation. These reports are retained as a negative methodological result,
not as a workload-sensitive gate-level power claim.

### Gate-level simulation status

The repository now includes a flat-port AES GLS harness and a model-explicit
runner. The available Sky130 functional and primitive cell models were found,
and Icarus now compiles and runs the mapped AES netlist to completion after
defining the model's empty `UNIT_DELAY` macro. A first direct gate-level VCD
annotated 154,059/154,059 pins and produced OpenSTA total power
`0.02861616946757 W`. The flat harness includes a 2,000-cycle handshake
assertion to classify deadlocks without imposing a wall-clock experiment cap.
Verilator still hits an internal code-generation failure on this model
closure, so the reproducible GLS runner uses Icarus for this Sky130 view.

The analogous AXI GLS runner compiles the mapped DMA netlist with Sky130
functional cell models and completes the existing coupled cocotb protocol
harness (8 transfers in the probe workload). A second `memory_map` pass after
flattening removes residual unpacked FIFO arrays from the emitted Verilog, so
the waveform is now OpenSTA-readable. The probe reports `0.02201835066080 W`
with 36,292 annotated pins and 4 unannotated pins. This is a gate-level probe,
not yet a comparative policy result.

- `make verify`: 209 tests passed, one skipped; Ruff clean.
- `make research-smoke`: passed.
- `make container-smoke`: passed, including FuseSoC/Ibex source preparation
  and deterministic workload compilation.
- Containerized `make verify-ibex` now passes with a generated 10,000-instruction
  floor-compliant workload: compilation, simple-system simulation, waveform/
  counter artifact creation, and three-input provenance verification all
  succeed. This closes the Ibex RTL simulation/activity artifact boundary, not
  the separate mapped-netlist/OpenSTA boundary.
- A fresh single-container AES run using the Docker Slang frontend completed
  synthesis and OpenSTA evaluation: 38 useful blocks, synthesis-weighted total
  power `0.02159873023629 W`, 608 clock edges, and per-cycle/window activity
  artifacts. `verify_artifact` passed. Annotation was sparse (203 annotated
  versus 153,020 unannotated instances), so this is reproducibility and
  relative-search evidence, not signoff-accuracy power.
- A fresh single-container AXI-DMA run completed synthesis, coupled
  source-to-destination simulation/activity generation, OpenSTA, and generic
  artifact verification (`valid=true`, `inputs_checked=3`). The result carries
  the explicit 4,096-byte useful-work value and hashes for its waveform,
  synthesis manifest, and Liberty; it is an end-to-end pipeline result, not a
  standalone comparative claim.
- Both checked-in Liberty files contain `internal_power`, rise/fall power,
  leakage, capacitance, and clock-gating characterization.
- The AES Sky130 mapped netlist coverage check matches all 43,619 cell
  instances across 72 distinct cell types to the Liberty (`instance_coverage`
  = 1.0); reproduce with `make check-liberty-coverage`.
- AES cross-PDK corpus: the archived 10-workload corpus at
  `out/aes-pdk-rank-20260831/corpus` validates against its paired Sky130 and
  Nangate45 report roots with Spearman ρ=`0.9999999999999998` (10 shared
workloads); see `out/aes-pdk-rank-20260831/corpus-validation.json`.
- The archived temporal cross-PDK diagnostic reports Spearman ρ≈`-1.0` across
  four shared schedules (`out/aes-temporal-cross-pdk.json`), indicating a rank
  inversion rather than agreement. It is excluded from validation claims until
  the temporal workload/report pairing is independently reconciled. The paired
  means are Sky130: `low_high_low=0.01852035`, `high_low_high=0.01848644`,
  `burst=0.01915642`, `ramp=0.01844827`; Nangate45:
  `low_high_low=0.00504285`, `high_low_high=0.00505190`,
  `burst=0.00499004`, `ramp=0.00506829`. The inversion is therefore a
  PDK-dependent temporal diagnostic, not evidence of cross-PDK agreement.
- A fresh containerized AES cross-PDK run also completes both Sky130 and
  Nangate45 synthesis/OpenSTA passes, with waveform and Liberty hashes recorded
  in `out/aes-cross-pdk/comparison.json`. Its single-workload annotation is
  sparse (0.132% Sky130, 0.136% Nangate45), so it is provenance evidence rather
  than a broad cross-PDK power claim.
- In the production container, the core-only Slang frontend probe succeeds
  with `IBEX_TOP=ibex_core` and 96 elaborated sources. A subsequent Sky130
  mapping attempt reaches the synthesis flow but did not complete in the
  observed run; a Nangate45 attempt likewise did not complete. The probe now
  runs without an application timeout, so these are unfinished runs rather
  than timeout-classified results. No mapped netlist or Ibex power result is
  claimed; manifests retain source and Liberty hashes for reproduction.
- `make vertex-preflight` passes with project `agcws-507604`, model
  `gemini-2.5-flash`, and the frozen prompt hash. A one-slot AES scalar Vertex
  smoke produced a valid workload and reached the activity evaluator, recording
  450 input tokens and 136 output tokens. An initial eight-slot call also
  confirmed malformed batches consume all requested proposal slots. This is a
  plumbing smoke, not comparative evidence.
- `make analyze-baseline BASELINE_DIR=out/aes-baseline-matrix-complete
  ANALYSIS_DIR=out/final-analysis` completes successfully, producing 25
  policy-target groups (125 run summaries across five policies and five scalar
  targets) and a reproducible convergence figure. This verifies the analysis
  tooling; it is not the undeclared multi-design final study.

## Preliminary AXI-DMA activity calibration

The corrected coupled-harness calibration combines three random seeds and is
stored at `out/axi-dma-calibration-corrected-3seed.json`: 48 valid proposals,
16 distinct activity values, and an observed activity range of
`19.67403066–19.80286242` total transitions per clock edge. Workloads are
non-overlapping, in-bounds, and satisfy the 4,096-byte useful-work floor.
These are activity-proxy bounds, not synthesis-level power bounds; they are
not yet used to claim a completed DMA comparative study.

The pacing-enabled generator was calibrated separately with 20 fresh random
workloads. All 20 passed validation and produced 20 distinct activity values;
the range widened to `12.38400853–19.90410309` transitions per clock edge.
This is the corrected envelope for future DMA activity searches. It varies
back-to-back, lightly gapped, bursty, and sparse descriptor schedules while
retaining the 4,096-byte floor and AXI 4-KiB legality rules.

A direct AES GLS runtime probe on the largest fresh calibration workload
(238 blocks) exceeded 13 minutes and generated a 220 MiB VCD before being
stopped. This confirms that GLS/OpenSTA belongs in the finalist tier rather
than the inner loop; a complete 20-workload proxy-to-gate correlation must be
run as a separately budgeted validation experiment.

The one-block RTL activity smoke measured 3.42 s wall time including the
initial Verilator build and produced a 19.5 MiB VCD. The existing one-block
GLS probe completed, but the full calibration DSL is not replayed by that
harness: data patterns and inter-block timing are not equivalent. Therefore no
proxy-to-gate correlation is reported yet; GLS/OpenSTA remains finalist-only
validation rather than an inner-loop evaluator.

The GLS harness now accepts the workload's block count, pattern, key length,
direction, and aggregate pacing. A 221-block replay compiled and launched with
those controls, reached 307 MiB of VCD after about five minutes, and was
stopped manually. This confirms exact replay is available but unsuitable for
the inner loop or a full smoke matrix; correlation must use a deliberately
bounded finalist corpus and report that scope.

The earlier one-block bounded run reported ρ=`0.0968280607`; it is superseded
because constant projection removed the corpus's block-count variance. The
correlation tool now supports the preregistered ladder of 1, 2, 4, 8, 16, and
32 blocks and parses OpenSTA dynamic power as internal plus switching power,
excluding leakage. The full ladder run is pending; no constant-projection
correlation is used as evidence.

The corrected recomputation uses each GLS VCD's own clock span, but retains the
declared rate-vs-rate comparison: RTL transitions per cycle versus GLS dynamic
power. Over the 34 completed rows, pooled ρ=`-0.7169173149` and block-controlled
partial Spearman ρ=`-0.1168103321`. Per-rung correlations are `-0.0990` (1/2
blocks), `0.2970` (4/8), and `0.2962` (16/32). These are partial diagnostics,
not a final 20-workload result; the values show that length/window effects are
not sufficient evidence of proxy validity.

An initial ladder attempt was stopped after 34 complete matched rows: it had
run for about 2h45 locally and was still processing the 16-block rung. Its
partial pooled diagnostic was ρ=`-0.7169`, but it is not a result because the
ladder was incomplete. This invalidates the earlier estimate that 32-block GLS
would fit comfortably under a minute and motivates trace reuse or an explicitly
bounded validation budget before final correlation claims.

A calibrated five-policy smoke matrix at 20 proposal slots is stored at
`out/axi-dma-matrix-calibrated-seed0/`, with an aggregate at
`out/axi-dma-matrix-calibrated-seed0-aggregate.json`. All 100 proposal slots
ran validly through the coupled Docker oracle; no policy reached the primary
0.05 tolerance within this short smoke budget. This is orchestration evidence,
not a comparative result.

A second seed has since completed the same matrix. The two-seed aggregate is
`out/axi-dma-matrix-calibrated-2seed-aggregate.json`: 5 policies × 20 slots ×
2 seeds, 200/200 valid simulations, and zero solves. The preregistered 200-slot
DMA comparison remains outstanding; these short runs only validate stability
of the calibrated orchestration.

The first full-budget calibrated DMA run is stored at
`out/axi-dma-matrix-calibrated-200-seed0/`, with aggregate
`out/axi-dma-matrix-calibrated-200-seed0-aggregate.json`. At 200 proposals,
random reached tolerance at evaluation 51 and offline-hybrid at 101; mutation,
evolutionary, and one-shot-agent were unsolved. All five arms completed 200
valid simulations with no validity-stage failures. This is one seed on one
activity oracle and is preliminary evidence, not a general policy ranking.

A five-seed full-budget matrix is now complete across the five policies, with
200 proposal slots per policy and seed. Paired inference is recorded at
`out/axi-dma-inference-5seed.json`; the panel remains small and underpowered for
definitive policy claims, and the result is still limited to the AXI DMA
activity oracle rather than the full multi-design study.

Held-out profile-arm Docker smokes also complete end to end. The temporal run
(`out/aes-temporal-heldout-20260901/`) used an achieved target manifest with 8
coarse windows and produced 8/8 valid simulations with 2,444 per-cycle samples;
the compositional run (`out/aes-compositional-heldout-20260901/`) likewise
produced 8/8 valid simulations against an achieved region-share target. Neither
short smoke solved its target. These validate profile plumbing and provenance,
not the full G4 comparison.

A larger one-seed profile run is also complete. The temporal arm at 32
proposals (`out/aes-temporal-heldout-20260901-seed1/`) produced 32/32 valid
simulations, retained 2,425 per-cycle samples per candidate, and reached its
achieved target within budget. The compositional arm
(`out/aes-compositional-heldout-20260901-seed1/`) produced 32/32 valid
simulations with 672 per-cycle samples per candidate but did not reach its
target. This is a G4 plumbing/milestone result for one target and one seed,
not a comparative profile conclusion.

Machine-readable aggregates for this snapshot are
`out/aes-temporal-pilot-aggregate.json` and
`out/aes-compositional-pilot-aggregate.json`. The aggregation command recovers
target identity from archived `target.json` files, preserving four temporal
target groups and five compositional target groups with three-run denominators
and deterministic bootstrap summaries.

The profile smoke was expanded to three seeds at 32 proposals per seed. Across
the temporal arm, 96/96 simulations were valid and 2/3 seeds solved the same
held-out achieved target. Across the compositional arm, 96/96 were valid and
0/3 seeds solved its held-out region-share target. Every run retained per-cycle
activity and target provenance. This remains one target per class and is not a
general profile-method conclusion.
The original temporal manifest contained one target, but the source corpus
contains four achieved schedules. A deterministic two-target manifest is now
recorded at `out/aes-temporal-targets-2.json`; the newly executed `burst` target
covered three seeds (96/96 valid simulations), with aggregate
`out/aes-temporal-burst-3seed-aggregate.json`. The reported profile evidence
therefore spans two achieved temporal schedules, while the compositional snapshot
now covers targets 0 and 1. Target 1 has aggregate
`out/aes-compositional-target1-3seed-aggregate.json` with 96/96 valid
simulations and 0/3 solves. The compositional target set still has additional
unrun achieved targets.

An older compositional pilot record referenced targets 2, 3, and 4 from a
superseded corpus. Those artifacts are not the current policy matrix and are
not used for its claims. The current machine-readable manifest contains three
targets, all of which are covered by the policy matrix below. The repeated AUC
values across these nearby region-share goals indicate that the current
32-proposal activity budget is not separating them; they are not evidence of
target generality.

The remaining achieved temporal schedules are now covered as well: `high_low_high`
and `ramp` each ran for three seeds at 32 proposals, with 96/96 valid
simulations and 0/3 solves for each. Their aggregates are
`out/aes-temporal-target2-3seed-aggregate.json` and
`out/aes-temporal-target3-3seed-aggregate.json`. The temporal pilot therefore
covers all four achieved schedules, 384 valid simulations total, and 2/12
seed-target solves across the two schedules already reported plus these two.

The profile-policy seam was then exercised on all four achieved temporal targets:
`out/aes-temporal-policy-matrix-20260901-v2-aggregate.json` contains five
distinct policies, three seeds per target-policy cell, and 32 proposal slots per
run. The matrix has 20 target-policy groups and 1,904 valid trials out of 1,920
proposal slots; it is a preliminary four-target activity comparison, not the
full preregistered profile factorial or a gate-level power result.
Paired policy inference for this matrix is recorded in
`out/aes-temporal-policy-inference-32.json`; each comparison has three matched
seeds per achieved target and Holm-adjusted p-values. The panel is too small for
definitive policy claims.
The corresponding convergence figures are
`out/figures/temporal-policy-convergence.png` and
`out/figures/compositional-policy-convergence.png`.

The corresponding compositional comparison is archived at
`out/aes-compositional-policy-matrix-20260901-v2-aggregate.json`: three achieved
region-share targets, five policies, three seeds, and 32 proposal slots per
run. It contains 15 target-policy groups and 1,434 valid trials out of 1,440
proposal slots. This is preliminary AES activity-oracle evidence, not a full
multi-design or gate-level result. The manifest contains three targets; older
notes referring to five targets describe a superseded corpus and are not part
of this matrix.

The rerun at the preregistered profile budget is archived at
`out/aes-compositional-policy-matrix-20260901-300-aggregate.json`: the same
three achieved region-share targets, five policies, three seeds, and 300
proposal slots per cell. It contains 15 target-policy groups and 13,410 valid
trials out of 13,500 proposal slots, with no profile-audit errors. This remains
preliminary AES activity-oracle evidence, not a multi-design or gate-level
result; the corresponding figure is
`out/figures/compositional-policy-convergence-300.png`.
Paired policy inference for this matrix is recorded in
`out/aes-compositional-policy-inference-300.json`; each comparison has three
matched seeds per achieved target and Holm-adjusted p-values. The panel is too
small for definitive policy claims.

The five-seed full-budget aggregate is
`out/axi-dma-matrix-calibrated-200-5seed-aggregate.json`, with paired inference
at `out/axi-dma-inference-5seed.json`: 5 policies × 200 proposals × 5 seeds.
This panel is still small and underpowered for definitive policy claims; use the
machine-readable inference for exact paired statistics.
The corresponding multi-root convergence figure is
`out/axi-dma-analysis-5seed/convergence.png`, generated from the five seed
roots with `analysis/plot_search_curves.py`.

## Preliminary AES scalar study

The verified AES scalar aggregate combines the original corpus with seeds 5
through 9 and is stored at `out/aes-analysis-10seed/aggregate.json`. It
contains five policies, five scalar targets, and exactly ten seeds per
policy/target cell (250 run summaries total). The corresponding convergence
figure is `out/aes-analysis-10seed/convergence.png`.

In this corpus, all policies solve the high target (`q=0.90`) at least once;
the recorded solve rates are random `1.0`, mutation `1.0`, evolutionary `1.0`,
hybrid `1.0`, and one-shot agent `0.8`. The lower targets have no recorded
solves in these runs. These are descriptive preliminary results, not a claim
that one method is superior: the corpus is AES-only, does not include the
other designs, and does not include Vertex-backed agent trials.

## Known limitations

## Fresh policy-independence smoke

On 2026-09-03, two-seed AES activity smokes were rerun after correcting policy
identity recording and the offline-agent fallback. The five declared arms
(random, mutation, evolutionary, offline-agent, and one-shot-agent) now appear
under distinct policy labels and produce distinct proposal streams. The
two-seed inference artifact contains paired comparisons for all non-random
arms; its p-values are descriptive because the smoke budget is only two
evaluations per seed and is not a preregistered final study.

The same rerun was completed for AXI DMA on 2026-09-03 with two seeds and 20
proposal slots per arm. All six arms completed: random, mutation, evolutionary,
offline-agent, one-shot-agent, and offline-hybrid. The aggregate contains paired
comparisons for each non-random arm; results are integration evidence only and
are not used as final statistical claims.

The fresh larger activity rerun also covered AES and AXI DMA with two new seeds
and 20 proposal slots per arm. The combined inference artifact contains four
paired design/seed instances for each policy shared by both designs, and two
for the AXI-only hybrid arm. These runs remain descriptive smoke evidence, not
the preregistered 5–10-seed final analysis.

- Ibex core elaboration, RTL/source closure, and standalone-core mapping are
  reproducible; simple-system wrapper mapping and Ibex gate-level power
  integration remain unsupported.
- DMA finalist OpenSTA reports have sparse activity annotation (about 1.31%
  for Sky130 and 0.77% for Nangate45 in the recorded run); they are retained
  as diagnostic evidence.
- Vertex credentials, exact model availability, and billing configuration
  are external prerequisites. No cloud-agent performance claim is made until
  `make vertex-preflight` passes and a real run records model and cost
  provenance.

The final report must replace this preliminary section only after the full
factorial run, statistical tests, finalist validation, and provenance audit
are complete.

## Memory-aware synthesis evidence

## Ibex core synthesis re-check

On 2026-09-01, a fresh Docker run of `make synthesize-ibex-core
IBEX_TOP=ibex_core` completed successfully after restoring portable defaults for
the optional FuseSoC and RISC-V tool variables. FuseSoC resolved 96 source files
and the Slang/Yosys mapping command returned zero. The earlier failure was not a
timeout: an empty exported `AGCWS_FUSESOC` value bypassed the resolver fallback.
The mapped core is still not a complete Ibex workload power pipeline; wrapper
closure and memory-compatible gate-level evaluation remain separate limitations.

## Ibex runtime activity evidence

On 2026-09-01, `make verify-ibex` completed in the verification container on a
fresh artifact root. The run compiled the generated RV32IM workload, executed
the FuseSoC simple-system simulator, converted its FST to a 19.2 MB VCD, and
produced a verified `activity.json` with 20,169 clock edges and nonzero
per-cycle toggles. The artifact verifier checked three input records and
returned `valid=true`. This establishes functional simulation and RTL activity
extraction for Ibex. It does not establish Ibex gate-level power: the
simple-system wrapper still lacks a verified mapped-netlist/OpenSTA path, and
the core-only netlist is not a drop-in replacement for that wrapper.

A five-sample calibration run (seed `20260901`) completed with every trial
above the 10,000-instruction useful-work floor. Its measured RTL activity
envelope was `75.47459106393761–76.16193221572304` total transitions per clock
edge. These bounds are suitable for activity-tier target normalization only;
they are not power-in-watts bounds and are not used as gate-level claims.

On 2026-09-03, a fresh ten-sample host calibration initially confirmed that
varying only instruction-stream length still produced a narrow
`75.5794185655843–75.9378289204592` envelope (0.47% span). The generator was
then changed to sample structured legal families (idle-heavy, ALU-heavy,
memory-heavy, and mixed). A fresh ten-sample calibration with that generator
passed the useful-work gate for every trial and widened the envelope to
`33.02092981603255–94.42136020261603` transitions per clock edge (186% span).
The latter is the calibration artifact to use for subsequent Ibex activity
experiments; the initial narrow result is retained as evidence of the prior
generator failure mode.

A fresh six-arm Ibex activity smoke (20 proposal slots per arm, seed `0`) then
completed with the widened calibration. All declared arms—random, mutation,
evolutionary, offline-agent, one-shot-agent, and offline-hybrid—completed their
isolated runs. The offline-agent history adapter bug found during this rerun
(the policy received `Trial` objects, not dictionaries) was fixed and covered
by the policy tests. This is a runner/integration validation artifact, not a
multi-seed statistical result.

Two additional Ibex seeds (`2`, `3`) were rerun at the same budget after fixing
the runner's policy-name serialization. The corrected summaries record
`offline-agent` and `offline-hybrid` explicitly; the earlier summaries using
the generic `agent`/`hybrid` labels are excluded from corrected inference.

The Ibex matrix entry point was smoke-tested in Docker with random, mutation,
and evolutionary policies at one proposal per policy using those bounds. All
three isolated runs produced one valid simulation with zero schema, protocol,
functional, or useful-work failures. This validates orchestration and artifact
separation only; it is not comparative performance evidence.

A three-proposal-per-policy Ibex pilot (seed `20260901`) then completed with
9/9 valid simulations across random, mutation, and evolutionary policies. The
activity-tier summaries are retained in the generated matrix format; this pilot
is intentionally too small for an inferential comparison and is not used as a
headline result.

A subsequent five-proposal-per-policy pilot with the same seed and calibrated
bounds completed 15/15 valid simulations across the same three policies. This
exercises history-dependent mutation and evolutionary proposals under a shared
budget; it remains activity-only and too small for an inferential claim.

The complete local Ibex arm set was also smoke-tested in Docker at one proposal
per arm: random, mutation, evolutionary, offline-agent, one-shot-agent, and
offline-hybrid. All 6/6 simulations were valid, with no schema, protocol,
functional, or useful-work failures. This confirms common-runner compatibility;
it is not comparative performance evidence.

An initial six-arm Ibex activity matrix (seed `0`, five proposal slots per arm)
completed with 30/30 valid simulations and zero failures at any validity stage.
The run used the calibrated activity bounds and shared proposal budget. It is a
preliminary activity-tier dataset; the sample is too small for inferential
policy claims and no gate-level power conclusion is drawn from it.

The first multi-seed Ibex activity dataset used seeds `1–3`, all six local arms,
and five proposal slots per arm. All 90/90 proposal slots completed valid
simulations. This confirms reproducible multi-seed orchestration and clean
validity accounting, but remains below the pre-registered 200-proposal budget
and is not a final policy comparison.

The first full-budget Ibex activity matrix used seed `0`, 200 proposal slots,
and all six local arms. All 1,200/1,200 proposal slots completed valid
simulations. The resulting activity-tier AUC summaries were random `2.9088`,
mutation `74.9344`, evolutionary `54.5826`, offline-agent `2.9088`,
one-shot-agent `11.7927`, and offline-hybrid `74.9344`; only random and
offline-agent reached the configured tolerance in this single seed. These are
descriptive activity-only results, not an inferential multi-seed comparison or
gate-level power claim.

Seed `1` of the full-budget Ibex matrix also completed with 1,200/1,200 valid
simulations. Its activity-tier AUC summaries were random `3.7176`, mutation
`15.3292`, evolutionary `3.0465`, offline-agent `3.7176`, one-shot-agent
`90.0793`, and offline-hybrid `15.3292`; random, evolutionary, and
offline-agent reached tolerance in this seed. These values remain descriptive
until the planned multi-seed aggregation is complete.

Seed `2` of the full-budget Ibex matrix completed with 1,200/1,200 valid
simulations. Its activity-tier AUC summaries were random `6.8117`, mutation
`35.1314`, evolutionary `22.4766`, offline-agent `6.8117`, one-shot-agent
`146.2547`, and offline-hybrid `35.1314`; random, evolutionary, and
offline-agent reached tolerance in this seed. These values remain descriptive
until the full seed set is aggregated.

Seed `3` of the full-budget Ibex matrix completed with 1,200/1,200 valid
simulations. Its activity-tier AUC summaries were random `4.2547`, mutation
`101.6232`, evolutionary `81.2774`, offline-agent `4.2547`, one-shot-agent
`77.3938`, and offline-hybrid `101.6232`; random and offline-agent reached
tolerance in this seed. These values remain descriptive until the full seed set
is aggregated. The run used an ephemeral container output root, so it is
recorded as audit evidence rather than a portable result archive.

Seed `4` of the full-budget Ibex matrix completed with 1,200/1,200 valid
simulations and persistent artifacts under `out/ibex-full/seed-4`. Its
activity-tier AUC summaries were random `1.8430`, mutation `2.7897`,
evolutionary `0.7075`, offline-agent `1.8430`, one-shot-agent `48.8044`, and
offline-hybrid `2.7897`; every policy except one-shot-agent reached tolerance
in this seed. This is still a single-seed descriptive result and activity-only;
the aggregation output has one run per arm and therefore is not an inferential
multi-seed comparison or a gate-level power claim.

Seed `0` was subsequently rerun with persistent output under
`out/ibex-full/seed-0` and completed with 1,200/1,200 valid simulations. The
activity-tier AUC summaries were random `2.9088`, mutation `74.9344`,
evolutionary `54.5826`, offline-agent `2.9088`, one-shot-agent `11.7927`, and
offline-hybrid `74.9344`; random and offline-agent reached tolerance. The
result is retained as a reproducible seed archive, but remains activity-only
and descriptive until the complete seed aggregation and gate-level validation.

Seed `1` was subsequently rerun with persistent output under
`out/ibex-full/seed-1` and completed with 1,200/1,200 valid simulations. Its
activity-tier AUC summaries were random `3.7176`, mutation `15.3292`,
evolutionary `3.0465`, offline-agent `3.7176`, one-shot-agent `90.0793`, and
offline-hybrid `15.3292`; random, evolutionary, and offline-agent reached
tolerance. The single-seed aggregate has no pairwise inferential comparisons;
this is reproducible activity-only evidence, not a gate-level power claim.

Seed `2` was subsequently rerun with persistent output under
`out/ibex-full/seed-2` and completed with 1,200/1,200 valid simulations. Its
activity-tier AUC summaries were random `6.8117`, mutation `35.1314`,
evolutionary `22.4766`, offline-agent `6.8117`, one-shot-agent `146.2547`, and
offline-hybrid `35.1314`; random, evolutionary, and offline-agent reached
tolerance. The persistent seed archive is reproducible activity-only evidence;
it does not establish a gate-level power claim.

Seed `3` completed with persistent output under `out/ibex-full/seed-3` and
1,200/1,200 valid simulations. Its activity-tier AUC summaries were random
`4.2547`, mutation `101.6232`, evolutionary `81.2774`, offline-agent `4.2547`,
one-shot-agent `77.3938`, and offline-hybrid `101.6232`; random and
offline-agent reached tolerance. The persistent seed archive is reproducible
activity-only evidence; it does not establish a gate-level power claim.

The complete persistent Ibex activity archive now covers seeds `0` through `4`,
with 1,000 valid simulations per policy and zero failures at all validity
stages. The five-seed aggregate and paired inference are stored at
`out/ibex-full/seeds-0-1-2-3-4-aggregate.json` and
`out/ibex-full/seeds-0-1-2-3-4-inference.json`. Mean AUC was random and
offline-agent `3.9072`, evolutionary `32.4181`, mutation and offline-hybrid
`45.9616`, and one-shot-agent `74.8650`; solve rates were respectively `1.00`,
`1.00`, `0.60`, `0.20`, `0.20`, and `0.00`. The paired activity-tier audit
found no Holm-adjusted significant difference at this sample size (minimum
adjusted p-value `0.3125`). These results remain descriptive activity-only
evidence because the Ibex wrapper lacks gate-level OpenSTA support.

The memory inventory and collateral path was validated on the current pinned
RTL closures. AES `aes_cipher_core` produced zero inferred memories. AXI DMA
produced 13 internal 32-entry FIFO memories with independent read and write
ports; the pinned BSG FakeRAM backend is single-port synchronous 1RW, so Yosys
rejects that mapping and the baseline remains unchanged. Ibex core inventory
produced four memories and two unique read-only geometries (32×32 and 16×3),
but their read ports are asynchronous (`RD_CLK_ENABLE=0`), which is also
incompatible with BSG FakeRAM's synchronous interface.

The integrated AES acceptance smoke was rerun after the five-seed Ibex update
with `make research-smoke`. It passed with synthesis-backed scalar evaluation,
determinism checking, activity extraction/plotting, and temporal and
compositional profile searches. The resulting bundle is under
`out/research-smoke/`; this is an integration checkpoint, not additional
comparative evidence.

BSG generation was run in an isolated checkout for the AXI and Ibex physical
geometries. CACTI-required padding is recorded explicitly as physical geometry
in the generated manifest; logical widths and depths are never silently
replaced. Generated collateral is reproducible diagnostic evidence, not a
claim that either design has been successfully macro-mapped.

Offline agent and hybrid summaries are tagged `heuristic_smoke_only` and are
excluded from policy inference. Only the Vertex-backed arm is eligible for the
cross-design agent claim.
