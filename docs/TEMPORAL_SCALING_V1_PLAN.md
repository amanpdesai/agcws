# Temporal scaling and stronger controls

2026-09-09. First milestone: CPU-only qualification. Freeze this file and the
qualification producer before simulation. Later comparative stages need separate
protocols; this document does not amend the completed depth study.

## What we measure today

Programmable Ibex, not AES, is the current development benchmark. A target is
eight **RTL bit-transition rates per clock edge** over a fixed 200,000-cycle
measurement interval. Each bin covers 25,000 cycles. Error is RMS residual
divided by the frozen scale 528.45376, not watts and not an envelope-clamped q.
Programs execute exactly 4,096 semantic body operations, with at most eight
segments and eight body operations per segment. Reset is outside the selected
observation. Release times are earliest-start polling deadlines, not guaranteed
phase boundaries, idle states, or durations. Actual phase placement is measured.

The legacy random generator already chooses segment counts, releases, work
allocations, instruction families and operands. It is not flat instruction
fuzzing. Stronger baselines should improve temporal sampling and structural
optimization, not be advertised as adding the first phase representation.

## Separate confirmation from extension

1. **Confirm the selected controller on fresh seeds, unchanged task.** Freeze
   Pro-4096, the entire current context/feedback contract, eight-bin targets,
   observation window and 128-slot budget. See the confirmation specification
   below. This is the next paid study, not a new model search.
2. **Qualify stronger baselines on development data.** Phase-random and a
   phase-aware GA use the same legal program language. First prove functional
   correctness, complete accounting and structural operator execution; then run
   a declared development comparison including Pro and both old controls.
3. **Qualify harder target families.** Generate requests deterministically,
   measure independent witness programs, and separate feasible instances from
   requests for which no witness has been found. Never cherry-pick targets by
   whether the agent wins. Keep witness programs out of every policy's context.
4. **Scale duration and resolution through a new evaluator version.** Do not
   relabel eight bins as thirty-two or multiply a waveform's time axis and call
   it a longer simulation. Pass equivalence and accounting gates first.
5. **New-family confirmation and cross-design transfer.** Fresh targets and
   seeds, frozen strongest baseline configurations; optionally Pro on DMA
   temporal. These are separate questions from seed replication on Ibex.

CPU-only qualification can proceed without viewing fresh confirmation outcomes.
No new paid call is part of this first milestone. Preserve all earlier studies
and the controller-selection history. A development win is not an instruction
to keep adjusting tests until a held-out win appears.

## Difficulty axes: vary one before crossing them

| Axis | Proposed levels | What must stay fixed / be reported |
|---|---|---|
| Duration | 200k, 400k, 800k cycles | Eight bins initially; report work and work/cycle, not just longer polling |
| Resolution | 8, 16, 32 bins | Initially 200k cycles; exact disjoint bin edges and integer counts |
| Shape | Flat control, periodic alternating, ramp, burst, random steps | Seeded generator, transition count, dwell widths, total variation |
| Amplitude | Prespecified normalized low/high bands | Freeze scale; qualification yield and achieved amplitude, no clipping |
| Transition density | 2, 4, 8 then more phases | Minimum dwell and actual completion; do not exceed representational support silently |
| Budget | 16/64/128 prefixes | Same trajectory per run; all baselines receive the same slots |
| Dependency regime | Operand/dependency and memory mixes | Same ISA subset and work legality, actual execution diagnostics |

Longer time is not automatically harder: it can add easy polling or make a
previously impossible completion feasible. More bins can expose timing errors
without adding expressive capacity. Independent uniform levels in every bin can
specify physically unreachable jumps. The request script therefore records
time, shape and scale separately and labels outputs `unqualified-request`.
Shape parameters apply only where meaningful: `phases` controls step families;
ramp, burst and flat report their actual transition count instead.

No dI/dt, voltage droop or resonant-frequency claim follows from activity bins.
Those need a calibrated power/current model, adequate temporal bandwidth and a
PDN model. Our eventual gate-power validation must preserve these exact bins.

## Feasibility and target selection

Maintain two objects:

- **Request:** generated desired values with seed, shape, bin edges, unit and
  normalization. It is not proof that a program can produce them.
- **Witness target:** an achieved, functionally checked waveform, measurement
  fingerprint, program/result hashes and useful-work evidence. Its source
  program is evaluator-only. A matching request is qualified only if measured
  residual is within the predeclared tolerance under identical units/windows.

Prefer a balanced witness pool from several non-LLM generators. Selecting only
one generator's outputs favors that generator's reachable distribution; the
small first smoke explicitly has that bias and is not an efficacy study.
Split construction seeds, development targets, search seeds and held-out target
families. Freeze selection rules without policy results, keep every attempted
construction and report qualification yield. Unmatched requests are unresolved,
not proven infeasible and not counted as policy failures in a feasible panel.

## Stronger controls

The new CPU controls are original adaptations, not GeST/SAGA reproductions:

- **Phase-random:** cycle through one to eight segments by proposal index;
  stratify releases into ordered cells spanning the first 75% of the window;
  independently sample weights, instruction families, body lengths and operands.
  Late completion can still fail; no hidden simulation/resampling repairs it.
- **Phase-GA:** best-eight valid archive, two-member tournament parents, bounded
  phase crossover and register crossover. Mutate release, weight, instruction,
  register, whole mix, phase order, insertion or deletion. Bootstrap until four
  valid observations; every eighth slot is a declared random immigrant. All
  parents come from prior batches; a batch cannot see its own observations.
- **Next candidates, not implemented here:** target-conditioned stratified
  sampling, differential evolution/CMA-style parameter tuning, and a
  surrogate-assisted mixed-variable GA. Select on separate development targets.
  Surrogate training must not leak witnesses or held-out outcomes; public
  evaluator calls, duplicates and failed candidates all count.

All policies retain the complete shared program language. An optimized bounded
parameterization is a useful expert baseline, but must be labeled as such and
its support compared with the full language. Record human tuning, population
size, bootstrap cost, mutations, restarts and hardware-specific code generation.
Do not compare an agent against a deliberately impoverished random generator.

## First milestone: bounded CPU qualification

Frozen inputs: existing v4 evaluator/binary/image and measurement fingerprint.
New producer: `experiments/temporal_scaling_v1/`. New analysis:
`analysis/temporal_scaling_v1.py`. No edits to historical producer sources.

1. Emit 25 seeded request objects: five families at (cycles,bins) =
   (200k,8), (400k,8), (800k,8), (200k,16), (200k,32), seed 901.
2. Generate exactly twelve phase-random witness proposals, RNG seed 820.
   Retain failures. Choose the first two valid achieved profiles with
   normalized max-minus-min at least 0.05. No replacement draws if this fails.
3. On those two targets, run legacy-random, phase-random and phase-GA at twelve
   slots, seed 830, batches of two, two identical charged initial programs.
   Total: 72 search slots plus twelve witness proposals; zero model calls.
4. Verify proposal reconstruction, parent visibility, CPU architectural state,
   count/rate/window arithmetic, witness selection, AUC and censoring. Compress
   compact evidence and track it; do not commit VCDs. Heavy data stays in out/.
5. Report qualification and operator coverage, not efficacy inference. Keep
   unsupported longer/resolved requests explicitly unsupported by this evaluator.

Pass means the qualification pipeline and operators work with at least two
witnesses, not that a particular policy wins. This tiny smoke does not select
baseline hyperparameters or touch fresh confirmation seeds.

## Confirmation specification — next paid milestone, not launched

Proposed fixed panel: six fresh RNG seeds 1000–1005, four existing achieved
Ibex targets, Pro-4096 versus original random, 128 slots, same two shared
initializations and batches of two. Check seed non-use and exact source/runtime
hashes, then freeze a dedicated protocol and manifest before calls. No prompt,
target, retry, allocator, measurement or model changes. Do not retrofit phase-GA
into this confirmation of the original Pro/random contrast.

This gives 48 trajectories / 6,144 slots and 1,512 Pro calls. At development
usage the Pro estimate is about $149.33, before uncertainty; a proposed $180
hard liability cap includes unresolved usage reservations. Verify cumulative
project spend and live model pricing before launch; remaining promotional
credit is not inferred from one experiment ledger. A cap stop is incomplete
data, not permission to omit cells or claim success.

Primary: two-sided exact paired sign-flip on six seed-level differences, each
averaging AUC over all four targets. One primary Pro/random contrast; targets
are not 24 independent replicates. Report effect sizes, seed-bootstrap CI with
small-n limitations, all cells, solve rate plus right-censoring, and equal-valid
secondary analysis. The smallest possible two-sided p is 2/64 = 0.03125;
do not claim high precision or equivalence. No efficacy peek/optional stopping,
seed extension or configuration repair based on these outcomes.

Fresh seeds test repeatability on known targets, **not unseen-target
generalization**. That broader claim needs the separately frozen generated-target
study. The model swap inside the Ibex depth study is controlled; comparing old
AES/DMA Flash studies with new Ibex Pro studies changes architecture, context,
target class and budget too. It is not a clean cross-design capability boundary.

## Longer-window implementation gate

Introduce one explicit measurement specification threaded through schema,
allocator, compiler, cycle guard, activity extractor, phase diagnostics,
prediction arrays, target loss, payload and cache fingerprint. No shared global
constant monkeypatching. Preserve the legacy mode bit-for-bit, then independently
test 400k/800k cycles and 16/32 bins: exact counts sum, boundaries, architectural
reference, useful-work completion and actual runtime. Fixed work and scaled work
are separate treatments. Record memory/storage growth and use clean --rm
containers. Only then qualify a new corpus; never reuse old normalizations or
cache entries under changed measurement semantics.

## Claim discipline

Success measures finite-budget discovery and target matching, not intrinsic DSL
expressiveness. Report target-family coverage, achieved transition density,
amplitude, phase alignment and gate validation where available. Faster search
does not prove a causal internal hardware model. Prediction directions have
three labels (−1, 0, +1), including a neutral band; 49.4% is not automatically
chance. Add observed/predicted marginals, majority and neutral predictors, and
seed-stratified confusion matrices before interpreting that diagnostic.
