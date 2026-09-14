# Exact-budget arithmetic feedback v5

Engineering intervention prompted by v4's recorded AES/DMA failures. It does
not change targets, workload grammar, legality gates, model or proposal budget.
No new paid run is authorized or implied by implementing this intervention.

For fixed-work schedule adapters, annotate visible history with exact totals,
repeat-weighted operation count and signed `required_minus_actual` values for
work and idle cycles. These are deterministic functions of the shared submitted
program and contract; they use no witness or target-specific search advice.
The helper is available to every policy. The model receives the derived values
explicitly so it need not infer subtraction from prose error messages.

Never change a submitted program, fill a remainder, emit a repair candidate,
award validity or score an invalid workload. Invalid shapes/nesting yield an
explicit unavailable diagnostic, not guessed totals. Count repeats analytically
without materializing unbounded expansion. Preserve best4/recent4 selection and
its bounded display rules. Mesh, Ibex and RedMulE do not gain invented fixed-sum
constraints. Existing v4 payloads and results remain frozen evidence.

Because runtime source inventory includes policy/helper code, this changes the
global measurement fingerprint. Before further paid checks, perform explicit
calibration and witness compatibility replay for each design, retain the bridge
evidence, and freeze a distinct follow-up protocol. Do not relabel v4 as passing.
The approval question about operational readiness with metered 504s remains
separate from this arithmetic-compliance intervention.

## Verification

The four new arithmetic/history tests and full 708-test suite passed. The
current-source compatibility replays passed for all five designs; Ibex also
repeated the full decoded-waveform comparison with creation-date exclusion.
All five versioned banks retain qualified requests and their original vectors.

`results/<design>/context-replay-v5.json` compares every one of the 126 recorded
v4 requests against current payload construction, schema provenance and parser
output. Mesh, Ibex and RedMulE are byte-identical; AES and DMA deliberately
differ. Those receipts do not relabel old model calls or erase API failures.
They avoid new paid calls solely for a changed global fingerprint on unaffected
controllers. Two additional context-replay rejection tests pass separately.

The synthetic 128-slot capacity check uses each design's largest observed valid
v4 program, not invented successful policy trajectories. All fit the existing
200,000-byte request guard: maximum guarded sizes AES 47,540, DMA 47,385,
mesh 41,025, Ibex 93,793 and RedMulE 21,360 bytes. Evidence:
`results/benchmark_readiness_v1/context-capacity-v5.json`.
