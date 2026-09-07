# V3 temporal development — running

The integral-number CPU equivalence gate passes: identical emitted assembly,
architectural state, markers and activity bins to the v2 partial-iteration case.
The retirement feedback uses exactly the same observation interval.

This directory does **not** yet contain a completed ablation. The 72-cell study
was frozen at `dca1344` before model calls and is running in supervised workers.
See [the protocol](../../docs/IBEX_TEMPORAL_V3_DEVELOPMENT.md) and `manifest.json`.
No completed v1/v2 result has been modified. Completion requires the full panel
and its independent compact-data audit, not just this feasibility gate.

At completion the compact archive will retain every run, frozen source,
context receipt and evaluation record. Copied RTL retains its original license
headers; its license will be included as `RTL_LICENSE` beside the context bundle.
Large simulator waveforms and retirement traces remain local scratch.
