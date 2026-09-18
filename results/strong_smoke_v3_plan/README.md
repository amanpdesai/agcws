# Gemini 3.8 MEDIUM/64k compatibility smoke

Completed: [outcome.json](outcome.json). Ten STOP responses, zero API errors,
zero MAX_TOKENS, all usage accounted. Saved same-cell feedback, measured rates,
loss/gate arithmetic, container/source equivalence and restart accounting were
checked without new simulations or API calls. Provider intervals do not overlap.

| Design | Valid generated / 4 | Round 1 / 2 valid |
|---|---:|---|
| AES | 2 | 0 / 2 |
| DMA | 4 | 2 / 2 |
| Ibex | 4 | 2 / 2 |
| Mesh | 4 | 2 / 2 |
| RedMulE | 2 | 2 / 0 |

The strict per-batch validity gate does **not** pass: AES's first batch was
protocol-invalid (corrected on the second); RedMulE's second failed useful work.
All four invalid model proposals were charged and received no scores. One
shared initial Ibex proposal also failed useful work; it is retained and charged
under the same initialization contract as the baselines. An explicit
request to accept audited operational readiness (at least one valid model
workload/design plus feedback/accounting, not a valid proposal in every batch)
is pending. Do not relabel the strict gate as passed or launch the full panel.

Known-token estimate and conservative liability both equal **$0.67590675**,
averaging **$0.067590675/call**. At that average, exhausting 28,350 calls is
**$1,916.20** before credits. This is not a forecast or an invoice: the smoke is
ten calls on observed targets, early stopping reduces calls, and longer histories
can change usage. Aggregate provider latency was 965.0 seconds. At serial
admission and that latency, exhausting every call would be about 31.7 days;
that is a throughput warning, not an ETA. Full-run concurrency needs an explicit
decision rather than assuming this conservative smoke setting scales cheaply.

820 tests pass; lint clean. Exact-byte verified archives:
[AES](../aes/strong-smoke-v3/), [DMA](../dma/strong-smoke-v3/),
[Ibex](../ibex/strong-smoke-v3/), [Mesh](../mesh/strong-smoke-v3/),
[RedMulE](../redmule/strong-smoke-v3/). No additional calls or cleaner reruns.

One alternating target and seed 9100 per design, six slots: two shared initial
programs plus two model batches. Ten API calls maximum, $2/design pause caps.
No early stopping, so the second call sees measured feedback. No replacement
calls for errors and no repair or fallback model.

[Preparation](preparation.json), [protocol](../../docs/STRONG_MATCHED_V3.md),
[failed 8k smoke](../strong_smoke_v1_plan/README.md),
[failed 32k smoke](../strong_smoke_v2_plan/README.md).
All v3 outcomes are retained; this is not a paper comparison.
