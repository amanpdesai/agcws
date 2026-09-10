# GeST phase bridge v1 qualification protocol

2026-09-10. Freeze before CPU execution. Eight proposed slots, seed 840,
batches of two, first achieved target in `results/temporal_scaling_v1/targets.json`.
Unchanged Ibex 200k-cycle/eight-bin evaluator and useful-work gates. No model
calls, baseline ranking, hypothesis test or new target selection.

## Exact reuse and explicit adaptation

The bridge hash-verifies pinned GeST's Algorithm, Individual and Population
files. It compiles only the original tournament-selection, uniform-crossover
and replacement-mutation method syntax trees, unchanged, against the original
Individual/Population classes. This explicit operator capsule avoids importing
or executing hardware measurement dependencies; it is not the whole upstream
runner. Only the checked-in upstream hashes are accepted. No fit/policy fallback.
Upstream copyright/permission notices remain in the read-only submodule.

Eight homogeneous genes each carry a phase plus a register vector, memory seed
and active-phase count. Locus zero supplies the globals/count; the first count
phases decode to the existing program DSL. Metadata in other loci and inactive
phases are neutral until crossover moves/activates them. All existing legal
programs round-trip; padding repeats existing phases, not extra executed work.
The neutral genotype is retained across feedback rather than regenerated.
This representation changes search geometry and is explicitly a GeST phase
adaptation, not published GeST reproduced on its original instruction encoding.

Mutation templates sample legal programs with the existing generator and use
one selected phase plus globals/count. This is the adaptation of instruction
operand mutation to phase genes; upstream replacement probability remains 0.2.
Uniform exchange is 0.5, crossover always runs, tournament size is two with
replacement over the eight best valid historical individuals. Ties retain slot
order. Fitness is negative measured temporal error; no roulette/logarithmic
predictor is used. Until two valid observations exist, bootstrap emits two
random programs. Rejections consume slots and do not receive fitness. This is
an explicit initialization rule, not an exception-triggered substitute policy.

## Accounting and safety

Ask returns exactly two proposals and charges both immediately. Only positive
even budgets are supported; odd budgets are refused instead of creating and
discarding an extra child. Tell requires the complete matching batch, finite
nonnegative losses for valid results and reason/stage with no score for invalid
results. Pending asks cannot overlap; tell validation is atomic. Children are
deep copies; the upstream full evolution method with parent aliasing is not used.
No candidate sees feedback from its own batch. Duplicates count even on cache hits.

The runner freezes producer hashes, upstream hashes, witness and runtime identity,
commits the manifest before execution, checkpoints each proposal batch before
simulation and resumes by deterministic reconstruction. One process lock guards
the run. Compact evidence excludes waveforms; retained CPU logs, compiled assembly
and profiles are independently checked with the existing depth evidence auditor.
Measured AUC comparisons and SAGA are outside this milestone.

Pass requires eight accounted slots and at least one upstream-operated proposal
actually evaluated. Validity and failure reasons are reported without replacing
unsuccessful proposals. The result does not select baseline hyperparameters.
