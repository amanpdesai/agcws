# AES corrective-feedback smoke v3

Complete: 54 cells, 864 charged slots, all eighteen requests, seed 8501. Every
target has an actual valid agent-generated workload in a later model call's
measured history. The frozen strict readiness gate passes 17/18, not 18/18.

One call on confirmation-alternating returned Vertex `504 DEADLINE_EXCEEDED`.
Its two slots were charged; there was no retry or fallback. Known estimated
cost is $1.5611813 with $0.10096 reserved for the call's unknown usage. Do not
report the unknown call as free or infer exact billing from this ledger.

`audit.json` records all calls, model identity, schema provenance, validity,
shared initializations and exact reconstructed feedback payloads. `evidence/`
retains responses, reservations, proposals and measured records. The original
six-slot v2 failure remains unchanged. This is plumbing evidence, not a
held-out performance study or a claim of perfect service reliability.
