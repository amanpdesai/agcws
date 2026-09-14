# DMA observation-window correction

The v2 corpus audit found at least 4,228.5 padded cycles in every measured
12,000-cycle trace, with identical idle values in both final bins. Those results
remain archived. Do not run more witness refinement or a paid study on that bank.

## Frozen timing diagnostic v1

Before choosing a replacement window, run twelve native programs under the
unchanged old measurement contract: 64 work units in groups of 1, 2, 4 or 8,
each with the exact 6,000 waits all before work, all after work, or distributed
uniformly among groups. Each case is one charged CPU measurement; no LLM calls.
The depth-one distributed case reaches the native 128-operation cap exactly.
All cases use the existing backend, Docker image, functional checks and cache.
Freeze the generated cases and driver hash before execution. Retain every result
including invalids. An unknown infrastructure error stops the diagnostic.

## Window selection rule — declared before diagnostic results

Require all twelve cases to be functionally valid. Choose the candidate horizon
as the maximum declared schedule-end cycle across these cases and the audited
v2 corpus, plus 256 cycles, rounded upward to the next multiple of 128. If this
is not shorter than 12,000, do not automatically shorten the window: investigate
the discrepancy. The corners are a timing diagnostic, not exhaustive proof over
the entire legal schedule language.

Apply a chosen horizon only as a new measurement version, after current
source-frozen Ibex runs finish. Verify the corners again under that horizon.
Workloads that cannot finish in the declared observation window must receive
an explicit functional rejection, never a power/activity score or fabricated
success. Keep unexpected tool failures distinct from workload rejection.

Regenerate calibration and both target banks using the original analytic shape
families, fixed mean-preserving construction and unchanged qualification gates.
Old v2 calibrations and witnesses do not establish admission under the new
window. New measured witnesses, archive audits and short Flash/baseline feedback
smokes are required before full-study readiness.
