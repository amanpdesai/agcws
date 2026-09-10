# Stronger-baseline development panel v1

2026-09-10. Freeze before target construction. CPU only. No Pro calls, held-out
claims, significance tests or baseline selection based on confirmation results.

## Target construction gate

Generate exactly four programs from each of three declared constructors:
original random (seed 860), phase-random (861), and scheduled-four-phase (862).
The third uses phase-random's four-phase bodies/registers with equal work weights
and releases at 0/40k/80k/120k. These are three construction distributions, not
three independent published algorithms. Keep all twelve attempts and failures.

Choose the first valid witness per constructor with normalized amplitude range
at least 0.05; require distinct waveform vectors. If any constructor has no
qualifying witness, archive the construction failure and do not launch the
panel. No replacement draws, threshold tuning or target selection using policy
outcomes. Freeze achieved target profiles before search. Witness programs are
evaluator-only and never passed to policies.

This balances constructor representation, not physical difficulty or workload
probability. It does not qualify arbitrary requested shapes, longer horizons
or higher resolution. Targets remain achieved eight-bin activity waveforms over
200k cycles, scale 528.45376 and tolerance 0.1, with unchanged useful-work gates.

## Panel

Three targets × two fresh development seeds (870, 871) × six arms × sixteen
charged proposals = 36 cells / 576 proposals. Complete full trajectories even
after tolerance; preserve prefix results without changing budgets. Target
construction costs twelve separate evaluations, never charged to search arms.

Arms: original random; phase-random; phase-GA; original GeST phase bridge with
two-proposal batches (`gest-batch2`); four-proposal no-screen GeST pool
(`gest-pool4`); temporal ridge screening (`ridge-screen`).

The primary descriptive contrast is ridge-screen versus gest-pool4. They share
seed, first four random programs, genotype, parent selection and offspring
operators. One measures every proposal; the other measures two of four after
bootstrap. Their trajectories may diverge after different observations. The
no-screen arm never fits a surrogate or pays a fitting cost. Test equality of
their first post-bootstrap candidate pools before running hardware.

The other four-proposal arms share the same first four initial programs.
`gest-batch2` deliberately retains the previous two-slot interface and only
shares the first two: it is a separately labeled feedback-granularity control,
not the matched screening contrast. Do not call these two GeST arms aliases.

## Accounting, metrics and failure handling

Every generated candidate counts, including filtered, duplicate and invalid
ones. Filtered validity and measured loss stay null. Fit/bootstrap failures stop
that cell, retaining the charged pending pool and an explicit incomplete flag;
no policy substitution or free retries. Infrastructure failures preserve
checkpoints and do not authorize new seeds. Any incomplete cell prevents a
complete-panel result. Other independent cells may finish for diagnosis.

Report best-so-far error AUC over proposal indices first, then solve rate with
right-censoring at 16, final error, measured validity, filtered count, selected
evaluations and cache hits. Before any valid result the curve uses the historical
1.0 sentinel, disclosed rather than interpreted as measured error. Filtered slots
carry forward the best measured error without being relabeled invalid. Equal-valid
secondary results use the per-target/seed common valid count and retain zero-count
instances explicitly. Two seed units support descriptive differences only.

Up to eight independent cells may run concurrently in disposable containers.
Cache identity is waveform/program/measurement based, not target based. Warm
cache hits depend on scheduling, so do not infer per-arm wall-clock or simulator
savings from them; selected-evaluator counts are the reproducible cost view.
Report unique cache misses globally. No witness outcome is inserted into a
policy's history even if its program happens to hit the cache.

Commit producer and manifest before construction, selected targets before search,
and compact complete evidence afterward. Replay proposals, parent visibility,
screening choices and metrics offline; independently validate CPU architectural
state, assembly, useful work and window arithmetic from retained records. Do
not commit traces. Frozen earlier studies and Pro confirmation stay untouched.
