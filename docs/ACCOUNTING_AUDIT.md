# Independent information and accounting audit

2026-09-12. Post-hoc verification of the known non-flat confirmation, not a new
held-out study. Freeze this checklist before computing audit outcomes. Preserve
every discrepancy; do not edit original records or loosen checks for agreement.

## Scope and independence

Restore the hash-verified `nonflat_temporal_v1` evidence. Audit all 36 cells,
4,608 slots, construction attempts and smoke records. Independent calculations
must not import original/current summary, loss, history or cost helpers. Read
the frozen protocol and inspect original execution code to identify semantics
and information paths, distinguishing this source review from independent
recalculation. Use standard arithmetic and a separately specified bootstrap.
This is not a waveform replay, external billing audit or proof of model cognition.

## Checks fixed before outcomes

1. Exact target × seed × arm panel; ordered slots 1–128; two shared charged
   initializations and 63 two-slot model batches per Pro cell. Count failures,
   malformed/short output, duplicates and cached evaluations without free slots.
2. Derive normalized RMS error from measured profile bins and frozen target/scale.
   Rebuild the discrete best-so-far AUC including invalid prefixes according to
   the declared implementation convention; disclose conventions absent from prose.
   Independently recompute solves, 128-censoring, validity, 16/64 prefixes and
   per-cell common-valid-count secondary results. Do not clip valid losses.
3. Reconstruct paired seed means, exact two-sided sign-flip p and percentile
   bootstrap CI using 10,000 seed resamples, RNG 1300. Compare numerical fields
   with a stated floating-point tolerance; retain differences, including RNG
   convention differences rather than choosing a favorable implementation.
4. Reconcile archived input/request/response/decoded/trial records and all known
   tokens/costs, unknown-usage reservations and cap arithmetic. Detect orphan or
   duplicate requests, hidden retries and missing terminal records where evidence
   permits. Separate observable transport calls from SDK-internal or provider-side
   attempts and local cost estimates from actual billed amounts.
5. Trace actual payload visibility: target, schema, semantic context, compact
   history and diagnostics. Check history against earlier same-cell raw trials,
   witness metadata/programs, construction/smoke contamination and cross-cell
   information. Classify shared vocabulary separately from literal leakage.
6. Reconcile evaluation IDs, repeated candidates and cache identities across
   policies, targets, construction and smoke; verify cached measurement contents
   against consumed profiles. Distinguish reuse from uncharged proposals and
   do not infer simulator execution counts without supporting cache/run logs.
7. Review original source for initial RNG handling, serialized requests, repair,
   filtering, retries, failure accounting, cache lookup and source/runtime pins.
   Independently verify qualification order, constant floors and distances using
   all archived witness outcomes, without regenerating workloads or running tools.

## Outputs and acceptance

Publish compact per-cell accounting, discrepancies, request/cost reconciliation,
information-access table, input/source hashes and limits under
`results/accounting_audit_v1/`. Findings belong in root `RESULTS.md` only.
Add hand-computed and adversarial fixtures for statistical/accounting helpers.
An audit completes by explaining discrepancies, not necessarily by finding none.
Any material unexplained discrepancy blocks new comparisons. No paid calls,
simulations, calibration changes or new target selection are authorized here.
