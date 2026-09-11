# Published evidence

Findings, statistics and claim limits live in the single root
[RESULTS.md](../RESULTS.md). This directory stores compact machine-readable
inputs, outputs, failures and provenance. It is not scratch.

| Evidence | Location |
|---|---|
| Completed non-flat Ibex confirmation | `nonflat_temporal_v1/` |
| Earlier scalar held-out comparison | `semantic_heldout_comparison.json` |
| Earlier structural/temporal held-out study | `structural_temporal_heldout_v1/` |
| Native-window gate power and arithmetic audit | `windowed_power_v1/`, `window_semantics_v1/` |
| Development model/depth studies | `ibex_capability_v1/`, `ibex_depth_v1/` |
| Stronger-baseline qualification | `gest_bridge_v1/`, `saga_temporal_v1/`, `baseline_panel_v1/` |

Subdirectory READMEs and launch records describe the original artifact context;
they are not independent current-status reports. Historical commands must run
from the [isolated source archive](../archive/README.md). `make archive-audit`
checks the completed non-flat panel with its original code, without cloud calls
or simulations. Other historical audit/report modules are retained there too.

VCD/FST and binaries are excluded from Git. Compressed trajectories retain
submitted programs, measured diagnostics and cost records needed for review.
Preserve immutable manifests and raw records; do not edit them to fit a claim.
The paper PDF is a historical draft until explicitly rebuilt from current results.
