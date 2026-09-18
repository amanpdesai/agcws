# Gemini 3.8 MEDIUM/64k matched matrix — prepared, not launched

**Pending operational signoff.** The smoke has no API/truncation errors and
16/20 valid generated workloads, but the strict per-batch validity criterion
fails. [Measured outcome and pricing](../strong_smoke_v3_plan/README.md).
User approval of a different operational criterion is pending; the scientific
every-bin ≤0.05 gate is unchanged. Budget and full-run concurrency also require
acknowledgement. No full-matrix provider calls have been made.

[Protocol](../../docs/STRONG_MATCHED_V3.md) and [preparation.json](preparation.json).
Five designs × nine profiles × ten matched seeds = 450 cells. Same tasks and
CPU/Flash-Lite evidence; explicit arm `strong-medium-64k`. The 65536-token
ceiling is user-approved. Full execution awaits readiness and launch approval.

Every design contains frozen config, manifest and hash-pinned launch contract.
Provider calls are serialized across sibling design runners; simulations remain
parallel. Caps are $120/design, not a verified balance or completion guarantee.

[Separate compatibility smoke](../strong_smoke_v3_plan/README.md). Historical
[v1 failure](../strong_smoke_v1_plan/README.md) and
[v2 failure](../strong_smoke_v2_plan/README.md) remain part of the evidence.
