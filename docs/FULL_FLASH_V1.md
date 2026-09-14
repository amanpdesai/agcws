# Five-design Flash study v1 — prepared, not authorized to run

Prospective configuration, 2026-09-14. Execution requires the completed readiness
audit and a separate user launch approval. Do not treat this document as a
completion receipt. Preserve all preceding smoke failures and costs.

Scientific task-quality audit is now in progress separately from operational
readiness. Do not execute this panel until that audit is resolved; see
[TASK_QUALITY_AUDIT.md](TASK_QUALITY_AUDIT.md). No frozen bank is silently changed.

## Panel and endpoint

Five designs: AES, DMA, Ibex, BaseJump mesh and longer-window RedMulE. Use the
existing confirmation split of each admitted bank: eight substantive profiles
and the separate flat control. Keep development cases out of this comparison.
All ninety bank requests have been exposed during engineering smokes; these
are fresh search seeds, **not unseen targets**, and this is not evidence of
generalization to an unseen target family. Do not call it task-held-out.

Ten paired seeds, 9100–9109, fixed before comparative execution. Three arms:
Flash-4096, phase-random and untuned phase-GA. This makes 1,350 cells, including
controls, with a ceiling of 172,800 requested proposal slots. The same seed,
target, initialization, grammar, measurement window, normalization and legality
checks apply within each matched comparison. No retuning after results arrive.

128 slots per cell; batch two, including two shared initial candidates.
Stop after the first batch containing a valid error ≤0.1, charging both
siblings. Keep the exact first-hit index; carry terminal best error forward
to slot 128 for the existing trapezoidal AUC endpoint. This is a stopped-policy
endpoint, not an estimate of further improvement from unexecuted proposals.
Unsolved cells remain in analysis, censored at 128, with solve rate alongside
evaluations-to-target. Invalid proposals have no score and still consume slots.

Primary: per-design paired difference in AUC, averaging the eight substantive
targets within each seed before inference. Report Flash versus each baseline,
ten comparisons total; two-sided exact sign-flip tests with Holm correction
across that family, plus paired seed bootstrap 95% CIs (10,000 resamples,
analysis seed 9200). Flat controls are a separately reported diagnostic, never
mixed into the headline mean. Report all designs regardless of significance.
Use the predeclared endpoint first, not the most favorable solve-rate cut.

Secondary: valid-evaluation analysis with common observed counts, stage-specific
validity, solved/censored counts, 16/32/64/128-slot prefixes, per-cell and
per-solve known USD, unknown liability and wall-clock. A zero solve count gives
undefined cost per solve, not zero. Price estimates are not cloud credit balance.
Any execution failures remain enumerated; incomplete cells cannot disappear
from denominators or be replaced with favorable seeds.

## Controller, resources and authorization

Flash is `gemini-2.5-flash`, thinking allowance 4096, temperature 0.7, top_p
0.95, output ceiling 16384. Runtime manifest pins source, image, schema and
model settings, including the prospective 600-second request deadline and one
SDK attempt. No fallback model, repair candidate or hidden retry.

Eighteen cell workers and one provider worker per design (five simultaneous
provider calls across the suite). All three policies share those execution
resources. Proposed liability ceiling: $120 per design, $600 total; these are
authorization caps, **not a spend prediction or verified balance**. At most
28,350 paid calls if no cell stops early. V4 smoke mean cost extrapolates to
about $434 across that many calls, but longer histories and API failures can
change it. Show the actual smoke cost and a conservative bound to the user
before launch. A ceiling exhaustion pauses execution without replacing cells.

The same baseline artifacts may support a later Pro comparison only if the
target vectors, scale, window, source/evaluator, grammar, seeds, initialization,
budget, batch size and stopping rules match exactly. A model-only change is
not permission to ignore a simultaneous measurement or controller change.
Pro is not part of this execution authorization.

## Remaining readiness gates

Finish the prospective AES/DMA feedback checks; operationally audit every
target and retained server error across all five designs. Preserve each strict
failure separately. Verify archives, durable resume/accounting/early-stop tests,
fresh seed inventory, and frozen configs. Only then request launch approval.
