# Bounded schedule history v4 — prospective runtime change

Prepared in an isolated worktree while the original RedMulE qualifications and
Ibex smoke run. Do not merge into the live runtime until those studies finish.
No new model calls are authorized by this document.

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
Full tests and real smokes remain required after integration.
