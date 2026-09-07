# Proposal interface v2 — development evidence

Status: allocator/compiler and CPU feasibility gate passed. The model comparison
has **not** run; this is not yet a demonstrated improvement in agent validity.

The gate covers partial iterations, allocations shorter than a body, conditional
control and memory effects. The embedded v1 witness reproduces its architectural
state, markers and all eight activity bins exactly. Gate inputs, emitted assembly,
architectural output and profiles are retained here; large FST traces remain in
the local artifact directory.

See [the protocol](../../docs/IBEX_PROPOSAL_V2_DEVELOPMENT.md). A new manifest and
prompt must be frozen before the proposed 36-cell model/baseline comparison.
No completed v1 result or source has been changed.
