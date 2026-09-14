# RedMulE per-bin witness construction v1

Frozen after the target-independent pulse diagnostic and before measuring any
target-directed candidate in this version. This is an expert feasibility
constructor, not a comparison policy or evidence of agent performance.

Keep the 262,144-cycle runtime, existing eighteen requested vectors, scale,
tolerance 0.1, nonflat margin 0.02, functional checks and useful-work floor.
For each size (4,8,16) and pattern (zeros,alternating,random), estimate marginal
transitions per additional job from the difference between the two queued
diagnostic workloads, divided by their job-count difference. This uses measured
activity, not the post-verification completion timestamps. The latter depend
on compiler decisions: one-job size16 calls a reference-check function, while
the two-job executable inlines it. Bus traces confirm the earlier reported
completion of two-job case is not an earlier first trigger.

For each requested bin, estimate jobs as `(rate - 2) * 32768 / marginal_area`.
Generate three complete schedules using floor, nearest-integer (half upward),
and ceiling rounding. Clamp negative counts to zero only because jobs cannot
be negative. Omit zero-job phases. All nonzero phases queue their jobs at
`bin_start + 2048`, duration 1, data seed 7500. Do not cap counts, move phases,
repair failures or discard duplicates. The shared validator/evaluator determines
legality and actual fit; queue spillover and start overhead are not assumed away.

Exactly 27 proposals per request, 486 total, at most 18 concurrent measurements.
All attempts including duplicates and invalid programs consume slots and remain
recorded. No adaptive adjustment or additional candidate selection is permitted
within this version. Select the lowest measured error per request, tie by case
identifier, and apply the unchanged qualification function. Predicted vectors
are never witnesses. If this fails, retain every failure; no target replacement.
