# Untuned phase-GA robustness extension v1

Declared 2026-09-12, after observing the confirmation results. This is a
**post-hoc robustness extension**, not fresh held-out confirmation. No simulation
or model call is authorized by this document. Scientific settings below are
frozen before execution; source and input hashes accompany the readiness bundle
in `results/evidence_extension_v1/`. Runtime identity and matched replay remain
execution gates, not completed checks.

## Question and comparison

Does the existing untuned phase-GA materially reduce the advantage observed
against phase-random when given 128 proposals? Use the three unchanged targets
in `results/nonflat_temporal_v1/targets.json`, seeds 1200–1205 and the same
eight-bin, 200,000-cycle, 4,096 semantic-operation task. Scale 528.45376,
tolerance 0.1. Do not modify usefulness rules, polling behavior or sub-bin
requirements after seeing the original solutions.

One new arm: `phase-ga`, 18 cells / 2,304 charged slots. Historical Pro-4096 and
phase-random are comparators only after measurement equivalence passes. There
are no new model calls and no stronger-model substitution. Do not tune the
operator probabilities, population or initialization on these observed targets.

## Exact control

Use `src/agcws/pipeline/policies/phase.py`, unchanged from the archived
`experiments/temporal_scaling_v1/baselines.py` behavior tested offline:

- Seed Python's local RNG with the cell seed. Charge two initial `random_program`
  draws identical to the confirmation; subsequent batches contain two proposals.
- Both proposals use history through the preceding completed batch. Never use
  an unmeasured sibling or a different cell's history.
- Bootstrap with phase-random until four valid parents exist; thereafter one
  scheduled immigrant at every slot divisible by eight.
- Elite archive is the eight lowest-loss valid records, ties by earlier slot.
  Two independent size-two tournaments select parents. Retain a random nonempty
  left prefix and a legal-length right suffix, bounded to eight segments.
  Independently inherit each register from the second parent with probability 0.5.
- Apply exactly one existing mutation: release, weight, instruction, register,
  swap, mix, insert or delete. Insert/delete eligibility depends on segment count;
  choices and step sizes are those in the source hash, not newly tuned parameters.
- All invalid, duplicate and cached candidates consume a slot. No dedup redraw,
  repair, filtering, surrogate or extra evaluation. Bootstrap/immigration are
  explicit algorithmic choices, not error recovery.

This is a custom phase-GA adaptation, not a reproduction of GeST or SAGA. It is
feedback-aware classical search, unlike phase-random. The agent's semantic prose
has no direct GA analogue; this tests a stronger algorithm, not equal semantic
comprehension or a causal mechanism.

## Measurement-equivalence gate

Offline readiness compares historical/current proposal sequences under mock
feedback, emitted assembly, reference state, allocation and all four metric
prefixes on archived cases. It does **not** attest a freshly executed simulator.

Before any new baseline measurement:

1. Verify the frozen binary, Ibex revision and container image ID from
   `parent_manifest.json` against the actual artifacts. Resolve the image to an
   immutable ID for invocation, not merely the old mutable tag. Capture compiler,
   extractor, runtime and all evaluator source identities. Missing artifacts or
   changed identities require explicit review; do not silently substitute.
2. Fix the live comparison set now: for each target and each original arm at
   seed 1200, select its first valid and lowest-loss valid program (ties by slot).
   Deduplicate by cache ID and record the complete selection before replay.
3. Replay that set with the maintained evaluator, without cache reuse. Require
   identical canonical program, emitted assembly, architectural registers/memory,
   operation allocation, window markers/duration, scoped integer bin transition
   counts and validity. Recomputed losses must agree within absolute/relative
   1e-10. Retain all traces and logs. No relaxed threshold after a mismatch.
4. If any comparison differs, halt the extension, diagnose and record it. Do not
   combine a new measurement regime with historical Pro scores. A fresh matched
   panel would require a separate execution decision.

Gate replays are validation cost, outside search N, never GA history. Frozen
witnesses remain hidden. Each target/seed has a fresh history; cache identity
must include the new fully recorded measurement identity. Log every cache hit,
miss, proposal and parent. Do not claim proposal equality means equal runtime.

## Execution and analysis

Run one foreground, durably logged cell at a time. Complete all 128 proposals
even after solving; checkpoint each batch. Infrastructure failures halt that
cell with its state preserved and are not workload-invalid scores. No outer
wall-clock killing, silent fallback or replacement seed. Resume only verified
state, and report incomplete cells instead of dropping them from denominators.

The maintained engine needs an explicit materialized study configuration with
the validated binary/image identity. Freeze that execution manifest before the
first measurement. No executable config with guessed paths is supplied here.

Primary extension endpoint: trapezoidal best-so-far error AUC on x=1..128,
127 intervals, initial value 1 until the first valid score; valid errors are
not clipped. Pair within target/seed, then average the three target differences
within each of six seeds. Report Pro-minus-phase-GA and phase-GA-minus-phase-random
contrasts, seed-bootstrap intervals and exact two-sided sign-flip tests, with
Holm correction across these two contrasts. State the six-seed resolution limit.
The original frozen inference remains unchanged.

Report solve rate with right-censored slots (128 for unsolved), validity by
stage, equal-valid secondary analysis, CPU time, wall time, cache reuse and model
cost (zero new model usage, not free compute). Show 16/32/64/128 prefixes only as
descriptive sensitivity, not extra hypothesis tests. The extension is useful
whether phase-GA wins, ties or loses; do not equate nonsignificance with equivalence.

## Mechanism studies explicitly separate

A simple division/polling scheduler is motivated by the solution audit, but its
construction and development tuning must be frozen separately. Correct-feedback
versus no-feedback and schema-only versus semantic-context arms likewise need
matched model/budget/targets and a new protocol. Do not add them silently to
this arm or optimize them on the confirmation outcomes. Independent target
qualification and fresh-seed confirmation follow the roadmap; those, not this
post-hoc extension, test broader generalization.
