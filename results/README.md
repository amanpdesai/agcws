# Published evidence

Findings, statistics and claim limits live in the single root
[RESULTS.md](../RESULTS.md). This directory stores compact machine-readable
inputs, outputs, failures and provenance. It is not scratch.

| Claim / evidence | Direct entry point |
|---|---|
| Scoped Pro versus phase-random confirmation | [summary](nonflat_temporal_v1/summary.json), [frozen targets](nonflat_temporal_v1/targets.json), [costs](nonflat_temporal_v1/cost_summary.json) |
| Earlier scalar held-out comparison | [comparison](semantic_heldout_comparison.json) |
| Earlier structural/temporal held-out study | [held-out evidence](structural_temporal_heldout_v1/heldout.json) |
| Native-window gate power and arithmetic audit | [windowed validation](windowed_power_v1/validation.json), [boundary verification](window_semantics_v1/verification.json) |
| Development model/depth studies, not confirmation | [capability](ibex_capability_v1/README.md), [depth](ibex_depth_v1/README.md) |
| Stronger-baseline qualification | [panel summary](baseline_panel_v1/summary.json), [GeST](gest_bridge_v1/), [SAGA](saga_temporal_v1/) |
| Post-hoc solution and measurement audit | [inventory](solution_audit_v1/README.md), [case notes](solution_audit_v1/case_notes.json) |
| Independent information/accounting audit | [reproduction and artifacts](accounting_audit_v1/README.md) |
| Budget/cost/coverage secondary analysis and readable suite | [reproduction and index](evidence_extension_v1/README.md), [analysis](evidence_extension_v1/analysis.json) |
| Untuned phase-GA robustness extension (in progress) | [execution and gate index](phase_ga_robustness_v1/README.md) |

Large nested trees are losslessly packed. See [verification and recovery](PACKED_EVIDENCE.md)
before using old per-slot paths. Published and development evidence are labeled
here rather than moved or discarded; all original evidence remains recoverable.

Subdirectory READMEs and launch records describe the original artifact context;
they are not independent current-status reports. Historical commands must run
from the [isolated source archive](../archive/README.md). `make archive-audit`
checks the completed non-flat panel with its original code, without cloud calls
or simulations. Other historical audit/report modules are retained there too.

VCD/FST and binaries are excluded from Git. Compressed trajectories retain
submitted programs, measured diagnostics and cost records needed for review.
Preserve immutable manifests and raw records; do not edit them to fit a claim.
The paper PDF is a historical draft until explicitly rebuilt from current results.
