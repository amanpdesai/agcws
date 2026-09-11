# Solution and semantic-mechanism inspection protocol

2026-09-11. Post-hoc audit of the completed non-flat temporal confirmation,
not a new held-out experiment. Aggregate outcomes are already known. Freeze
these rules in Git before inspecting program contents; commit the resulting
selection manifest before detailed interpretation. Findings belong only in
root `RESULTS.md`; this file defines method and scope.

## Selection

Use all 36 cells from `results/nonflat_temporal_v1/search_manifest.json`.
Within each complete 128-slot cell, select:

- First valid proposal with error <= the frozen tolerance (absent if unsolved).
- Best valid proposal (minimum loss, ties by lowest slot).
- Worst valid proposal (maximum loss, ties by lowest slot).
- First invalid proposal, if present.

Retain all role labels when selections coincide. Select using validity, slot
and loss only, not program appearance or explanations. Machine-readable checks
cover every cell and all submitted payload histories, not just examples.

Detailed human-readable inspection covers the lowest seed for every target
and policy, using its selected roles. If that baseline cell is unsolved, also
inspect the first solve at the lowest seed that solved that target, if any.
Do not replace inconvenient cases. All uninspected cases and missing artifacts
must remain identifiable. Reading programs cannot expose private model reasoning:
only emitted hypotheses, predictions, proposals and observable execution are available.

## Checks

1. Bind trials, payloads, responses and measurements to frozen inputs with hashes.
2. Compare submitted phase schedules and operations with execution diagnostics,
   retirement, independent functional references, observation window and useful-work definition.
3. Inspect first-solve versus best behavior; identify no-op/state-convergent work,
   active waiting and possible fixed-bin exploitation. Distinguish evaluator bugs
   from legal optimization of an underspecified objective.
4. Inspect actually sent payloads for hidden witnesses, constructor metadata and
   cross-cell/future history. Compare shared grammar vocabulary separately from
   actual leakage or asymmetric target-specific hints. A negative literal search
   is not proof of absence of conceptual alignment.
5. Re-bin available detailed-inspection best-candidate and target-witness traces
   at finer and shifted boundaries if the retained format can be read safely.
   Keep the original physical observation interval and state boundary convention
   explicit. Do not manufacture finer-resolution target vectors by interpolation
   and call them measured targets. Report unavailable traces and replay needs.
6. Evaluate whether emitted predictions and observed changes support plausible
   mechanisms; do not infer calibrated causal reasoning from successful output alone.

## Boundaries and output

No paid calls, new candidates, hardware replays or comparative runs in this slice.
Existing trace conversion and deterministic offline analysis are allowed. Do not
modify frozen evidence. Store selection, hashes, diagnostics and interpretive
case notes in a new compact audit directory. Unexpected evidence is retained,
not repaired to pass a check. Missing traces limit conclusions.

This slice does not replace the separately planned independent accounting audit,
128-slot phase-GA extension or fresh target-family confirmation. Its final output
must separate established observations, suspected mechanisms, unresolved validity
questions and proposed discriminating ablations (semantic context, feedback,
closed-loop depth and target-family change). An observational audit cannot
definitively establish semantic understanding as the cause of success.
