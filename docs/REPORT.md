# AGCWS report draft

This is a report scaffold, not a final result. Numbers may enter the final
report only from committed or archived manifests whose provenance passes
`make audit-reproducibility` and whose experiment coverage matches
`docs/EXPERIMENTS.md`.

## Abstract

AGCWS studies goal-conditioned synthesis of legal hardware workloads for
requested dynamic-power behavior. The final abstract must state which target
classes, designs, policies, and seeds were actually run. It must not describe
the current AES-only preliminary corpus as a multi-design result.

## 1. Problem and contribution

Frame the contribution as arbitrary scalar, compositional, and coarse temporal
goal conditioning over heterogeneous workload interfaces. Do not claim to be
the first power-virus or low/high-power workload generator. Prior-art status
must follow the verification legend in `docs/LITERATURE.md`.

## 2. System

Describe the CHIA node boundary, design adapters, four-stage validity gate,
proposal-counted budget, activity evaluator, finalist OpenSTA evaluator, and
telemetry ledger. Include the architecture diagram from `docs/ARCHITECTURE.md`.

## 3. Experimental method

Report the frozen prompt hash, exact model identifiers, sampling parameters,
seeds, budgets, tolerances, useful-work floors, simulator/synthesis/STA
versions, Liberty hashes, container digest, and validity accounting. Explain
that per-cycle toggle counts are a diagnostic/temporal-shape signal; OpenSTA
power is not a per-cycle measurement.

## 4. Results tables

The final version must include:

1. Full policy × design × goal × seed AUC and solve-rate table.
2. Validity rates split by schema, protocol, functional, and useful-work
   failure.
3. Cost, tokens, wall-clock, and evaluations-to-tolerance.
4. Finalist proxy-to-gate agreement and proxy exploitation rate.
5. Cross-PDK rank agreement with annotation coverage.

The dependency-free helpers in `agcws.analysis.inference` provide exact
paired sign-flip p-values, Holm adjustment, and matched-pairs rank-biserial
effect sizes for these comparisons. Bootstrap confidence intervals are
provided by `agcws.analysis.aggregate`.

Current AES scalar source: `out/aes-analysis-10seed/aggregate.json`, covering
AES scalar targets, five policies, and exactly ten seeds per cell. It is still
not the final multi-design factorial result.

Current DMA pilot sources are `out/axi-dma-matrix-calibrated-200-3seed-aggregate.json`
and `out/axi-dma-matrix-calibrated-200-3seed-inference.json`. They cover three
seeds at 200 proposals on the coupled activity oracle and must be labeled as a
preliminary single-design activity study. Current profile-arm evidence is
summarized in `docs/RESULTS.md`; it covers one achieved target per profile class,
not a full target factorial.

## 5. Figures

The current reproducible convergence figure is
`out/aes-analysis-10seed/convergence.png`. Final figures must be generated
with `make analyze-baseline` (or an equivalent recorded command) from the
complete declared corpus, and must include scalar convergence, temporal
profiles, compositional attribution, cross-PDK agreement, and validity/cost
breakdowns.

## 6. Limitations and negative results

State explicitly that DMA gate reports have sparse RTL-to-netlist annotation,
Ibex core source closure and RTL execution are supported but Ibex mapped
gate-level power is not currently established, and Vertex-backed comparative
runs require external project/model/billing configuration. These constraints
are methodological results, not reasons to substitute unsupported claims.

## 7. Reproduction checklist

- `make verify`
- `make research-smoke`
- `make container-smoke`
- `make chia-smoke chia-node-smoke`
- `make inspect-liberties`
- `make analyze-baseline BASELINE_DIR=<complete-run-root> ANALYSIS_DIR=<analysis-root>`
- finalist validation for every reported synthesis-level result
- provenance audit and archived manifests

## Finalization gate

Replace this scaffold with the four-page report only after the full factorial
study, profile-target study, statistical tests, finalist validation, and
Vertex/Ibex status decisions are resolved or explicitly recorded in
`docs/DECISIONS.md`.
