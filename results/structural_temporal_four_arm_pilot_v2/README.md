# Typed structural-edit development pilot v2

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

Eight matched-source AES cells: two achieved temporal reference profiles,
seed 310, 16 proposal slots per cell, batch size 4, fixed scale 200 and
tolerance 0.10. All valid workloads complete 64 AES-128 blocks over exactly
6774 clock edges. Compact ledgers, target manifests and original run manifests
are archived; all 128 requested slots passed the independent pilot audit.

| Policy | Mean AUC | Valid slots | Solved targets |
|---|---:|---:|---:|
| Random | 1.6546 | 32/32 | 1/2 |
| Structural evolution | 1.8228 | 32/32 | 1/2 |
| Typed-edit agent | 1.7927 | 28/32 | 0/2 |
| Typed-edit hybrid | 1.7602 | 30/32 | 0/2 |

Primary AUC is lower-is-better. This one-seed pilot does not establish an
agent advantage; random has the lowest mean AUC and neither agent arm solves
a target. Do not substitute validity improvement for search performance.

The agent generated 20/24 valid post-initialization proposals (83.3%), versus
5/24 (20.8%) in the full-schedule v1 pilot. Hybrid generated 14/16 valid model
proposals; its other 16 slots came from shared initialization/evolution.
All six v2 failures were unknown operator names or extra fields, rather than
parent/path errors, budget-total violations, or output truncation. They were
charged without repair and precise failures were retained in diagnostics.

V2 uses one typed structural operation per proposal, the same implementation
as structural evolution. Split/merge change sequence length; move/swap change
ordering; redistribution changes pacing. Parents are explicitly named and
each sequence entry indexed. Eight parents match the CPU population; v1 used
four, so the v1/v2 comparison is an interface-development comparison, not an
isolated causal ablation of one change.

Recorded cost is $0.0313543 with no unknown usage, versus $0.0928945 for v1.
V2 is usable for the next DMA transfer check, not selected or frozen for final
evaluation. Further selection must use both designs and fresh held-out seeds.
