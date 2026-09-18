# Gemini 3.8 v2 compatibility smoke

**Completed; readiness failed on Ibex.** [outcome.json](outcome.json) retains all
ten calls: one MAX_TOKENS, one server-side 429, eight STOP responses. Valid model
proposals: AES 4/4, DMA 4/4, Ibex 0/4, Mesh 4/4, RedMulE 3/4. Known-token cost
estimate $0.7260495, plus the unresolved-usage reservation for the 429; not a bill.

One alternating target and seed per design, two initial programs plus two
two-candidate model calls. Six slots/design, ten calls total, early stopping
disabled to exercise feedback. Same tasks, context and MEDIUM reasoning as v1;
only the output ceiling increases from 8192 to 32768 tokens.

[Preparation](preparation.json), [protocol](../../docs/STRONG_MATCHED_V2.md),
and [retained failed v1](../strong_smoke_v1_plan/README.md).
This smoke is excluded from paper comparisons; all failures remain evidence.

Exact-byte verified archives: [AES](../aes/strong-smoke-v2/),
[DMA](../dma/strong-smoke-v2/), [Ibex](../ibex/strong-smoke-v2/),
[Mesh](../mesh/strong-smoke-v2/), [RedMulE](../redmule/strong-smoke-v2/).
