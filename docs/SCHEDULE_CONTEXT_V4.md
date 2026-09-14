# Bounded schedule history v4 — prospective runtime change

Prepared in an isolated worktree while the original RedMulE qualifications and
Ibex smoke run. Do not merge into the live runtime until those studies finish.
No new model calls are authorized by this document.

## Corrective resource context

The DMA v3 confirmation-activation smoke produced 13 protocol violations and
one schema rejection across its 14 generated slots. Repeated exact-total errors
occurred despite actual/required totals in the validator's response. For all
exact-work schedule contracts, render numerical budgets and generic
budget-preserving refinement guidance: reorder a valid reference, or transfer
amounts between same-kind operations while respecting bounds and repeat
multiplicity. No target-specific example, witness, automatic correction or free
retry is added. Mesh and RedMulE do not receive fictitious exact-sum constraints.

This is interface development informed by all-target smoke failures. Both
named bank splits have been exposed to these smokes; a later fresh-seed study
must not describe the target vectors as previously unseen. Preserve the old
smokes and distinguish operational development from policy-performance claims.

## Failure and intervention

The offline repeated-valid-workload capacity test finds a reachable request-size
failure: AES/DMA/mesh full-history requests exceed the 200,000-byte guard before
64 proposals. This is a synthetic stress case, not a claim that a measured
trajectory already failed. Repeated proposals are legal and charged, so the
full 128-slot runner must tolerate such a history.

For schedule backends, use all rows when history has at most eight slots.
Otherwise retain the four lowest-loss valid trials (ties by slot) and the four
most recent trials, deduplicate by slot, then sort chronologically. Record the
selection version, shown slots, total slots and omitted count in every payload.
The full measured stream remains available to policy code and in the ledger.
This is the LLM policy's fixed context selection, not a change to GA history.
Ibex keeps its existing bounded notebook/context protocol unchanged.

A program longer than 12,000 encoded JSON bytes is omitted from the display,
with its SHA-256, byte count and explicit omission reason. A reason longer than
2,000 UTF-8 bytes is displayed as a marked excerpt with a full-content hash.
Neither operation changes the submitted program, its validity, its score or
charged slots. Full originals remain in artifacts. These display limits trade
away detailed context for unusually large past proposals; report that limitation.

The observation window, target bank, validation, simulator and classical
operators do not change. The implementation still changes the broad source
fingerprint, so publication/launch requires explicit runtime compatibility
evidence and a separately frozen all-target smoke before any full study.

## Verification before merge

Thirteen targeted tests pass: deterministic selection, no mutation/future rows,
explicit oversized-data handling, adversarial 128-slot request capacity, shared
feedback execution and early stopping. The same repeated measured workload
diagnostic now fits the byte guard on AES/DMA/mesh/RedMulE. This proves capacity
for those tested histories, not guaranteed provider success or target solving.
With pinned dependencies supplied, the complete isolated suite passes **693
tests**, with three existing warnings. The initial isolated run failed because
dependencies and the interpreter link were missing, and one parser test read
a historical `out/` waveform. That test now creates a deterministic waveform
with exact counts (16 clock edges, 48 transitions, eight bins of six), rather
than depending on ignored scratch data. No tests were skipped to obtain green.
Full tests and real smokes remain required after integration.
