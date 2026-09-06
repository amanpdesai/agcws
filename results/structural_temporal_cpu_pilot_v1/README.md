# Fixed-window AES structural CPU pilot

Four development cells: two achieved reference profiles (`random_300`,
`random_301`), random and structural evolution, seed 310, 16 slots per cell,
batch size 4. The reference workload itself was not passed to either policy.
All 64 proposals were valid and performed 64 AES-128 encryptions in exactly
6774 clock edges including reset. Each candidate contained exactly 6000
idle cycles. All four captured executable source digests match.

Scoring is fixed-scale capped NRMSE: `min(1, RMSE(raw bin rates, target)/200)`.
Tolerance is 0.10. No candidate-peak normalization or time warping is used.
Raw eight-bin rates, schedules, targets, manifests and ledgers are archived.
`analysis/archive_structural_pilot.py` independently reconstructs losses,
AUC, exact work/window checks, solves and right censoring before archiving.

| Reference | Random AUC | Evolution AUC | Random solved | Evolution solved |
|---|---:|---:|---|---|
| random_300 | 1.7536 | 1.6303 | No | Yes, slot 8 |
| random_301 | 1.5556 | 2.0152 | Yes, slot 7 | No |

Both methods solve one target. This tiny one-seed pilot demonstrates a working
structural temporal loop, not statistical superiority. It contains no agent
calls and costs no LLM tokens. Gate-power validation and DMA transfer remain
pending. Do not pool this activity profile endpoint with the prior scalar study.
