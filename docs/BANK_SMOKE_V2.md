# All-target readiness smoke v2

For each fully qualified, current-runtime bank: both splits, eight nonflat
targets plus the separate control, seed 8500, Flash-4096, phase-random and
phase-GA. Six slots per cell in batches of two: shared random initialization,
first generated batch, then a second batch with measured feedback. Disable
success stopping only for this plumbing test so the feedback call occurs.

Per design: 54 cells, 324 charged proposals, at most 36 Flash calls, a hard
five-dollar reservation ceiling, 18 cell workers and three provider workers.
No retries, fallback model, additional seeds or full-study launch. Retain raw
responses, parse failures, reservations and unknown usage. The qualification
receipt stays outside the payload; no witness program is given to a policy.

Audit shared initializations, exact regenerated payloads, requested-slot
accounting, costs and cached measurements. Every target must have an actual
valid agent-generated first batch feeding its second call before it can pass
the feedback gate. A successful process exit alone is not readiness. Report
all failures rather than automatically resampling. These are smoke observations,
not new held-out comparisons; seed 8500 must not enter paper inference.
