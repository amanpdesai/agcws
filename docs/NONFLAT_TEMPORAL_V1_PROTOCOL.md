# Non-flat Ibex temporal confirmation

2026-09-10. Freeze before target construction. This replaces the *priority* of
unchanged-target Pro/random replication, not its results. It tests fresh-target
generalization to one scheduled-program construction distribution. Earlier
development and held-out studies remain untouched.

## Construction, independent of policy outcomes

Generate exactly 24 scheduled-four-phase programs with RNG seed 1100 using the
existing constructor: random instruction families, operands and register state,
equal work weights, releases 0/40k/80k/120k. Keep every attempt and failure.
The unchanged v4 evaluator measures eight RTL transition-rate bins over 200k
cycles, 4096 semantic body operations, scale 528.45376 and tolerance 0.1.

In generation order, select the first three valid witnesses with best constant
vector error >= 0.20 and normalized RMS distance >= 0.15 from every previously
selected target. The constant floor is population standard deviation / scale.
Do not lower thresholds or draw replacements if fewer than three qualify: stop
before paid calls and report a qualification failure. Retain all candidates;
do not choose by search performance. Check CPU reference, assembly, execution,
integer counts and rates independently; commit targets before any search.

These thresholds exclude flat-solvable vectors but do not guarantee difficulty
or a particular waveform shape. Witness programs are never sent to policies.
The controller sees target rates, not construction metadata or archive paths.
Fresh witnesses from one known constructor are not arbitrary-shape generality.

## Frozen comparison

Three selected targets × six fresh search seeds 1200–1205 × two arms:
`pro-4096` and `phase-random`. 36 trajectories, 128 slots each (4608 slots).
Two identical charged initial random programs, then batches of two. Phase-random
uses its original slot-indexed one-to-eight-phase schedule, without tuning.
Pro uses the depth study's exact model settings, prompt, schema, compact history,
RTL-derived context and feedback tools. No model, prompt, repair, or retry tuning.
Both arms retain the same legal workload space and evaluator. Witnesses are
evaluator-only. Pro's slot allocation is not enlarged after malformed output.

All proposals, duplicates and rejections count. No automatic candidate repair
or replacement. Run all 128 slots even after a solve, retaining 16/64 prefixes
as secondary summaries. AUC on proposal index is primary. Unknown API usage
retains a conservative reservation; API failures consume their requested slots
and are reported separately from schema failures. Infrastructure failure or
model-version change halts execution with checkpoints, not a fallback policy.

CPU qualification before paid launch: first four slots of a phase-random
trajectory on the first selected target with separate seed 1190. No additional
target selection or hyperparameter tuning from that smoke; it tests compilation,
measurement, payload/schema wiring, archival audit and immutable resume only.
Its data is excluded from the comparison. Search seeds must be unused before
freeze. Maximum four workers, serialized paid calls, no detached shell workers.

## Analysis and stopping

Analyze only a complete panel. Primary contrast: Pro minus phase-random AUC,
averaged over the three targets within each of six seeds. Two-sided exact paired
sign-flip, one contrast, no multiplicity across exploratory cuts. Report the
mean difference, six seed differences and percentile seed-bootstrap 95% CI
(10,000 resamples, RNG 1300), noting small-n limitations. Minimum two-sided p is
2/64=0.03125. No interim efficacy checks, optional seed extension or retuning.

Secondary: solves and right-censored slots-to-tolerance (128 when unsolved),
validity by stage, equal-valid-evaluation best error within each target/seed,
per-target descriptions, 16/64 prefixes, tokens/cost. Shared cache warmth and
serialized inference mean per-arm wall-clock is not an equal-resource comparison.
Unfinished cells or a cap stop make the study incomplete, not omitted observations.

## Cost, execution and evidence

18 Pro trajectories × 63 calls = 1134 calls. Development-based estimate is
about $112, not a promise. User confirmed additional funding on 2026-09-10;
hard run liability cap $150. Current standard Vertex Pro prices checked against
[Google pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing):
$1.25/M input and $10/M output including reasoning for <=200k input tokens.
The depth metering implementation matches this schedule. No extra paid preflight
or retry calls. Auth/billing checks are read-only; first real call is a study call.

Freeze source/runtime, schema, target and protocol hashes before launch. Run
under a named user systemd service (linger enabled), no automatic restart,
with stdout/stderr log, PID, immutable request/batch/cell checkpoints, runner
lock and terminal success/failure record. Use process-based waits for CPU jobs;
do not poll model results to choose continuation. Archive compressed compact
evidence after each completed cell and perform full independent audit at end.
No trace files in Git; disposable Docker `--rm` evaluations. An interrupted
in-flight request cannot be silently resampled on resume.

This is activity-profile synthesis on Ibex, not gate-power or dI/dt evidence.
A positive result does not prove a causal internal model or wider DSL
expressiveness. The baseline was chosen from development data; the new bank and
search seeds are held out from controller/baseline tuning, conditional on the
predeclared feasibility filter.
