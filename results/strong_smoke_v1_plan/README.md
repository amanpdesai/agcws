# Gemini 3.8 pipeline compatibility smoke

**Failed:** eight of ten responses truncated at the 8192-token combined
reasoning/output ceiling. [outcome.json](outcome.json) retains every outcome.
This smoke is not a readiness pass. The original runtime is commit `65d0ed79e`.

Separate from the full panel: five designs, one alternating target and seed
9100 each, six slots (two initial + four model-generated), two provider calls
per design. Early stopping disabled to exercise measured-history feedback.
No tuning, repair or retries for a cleaner outcome. All results are retained.

[preparation.json](preparation.json) and per-design manifests freeze the smoke.
The full study's scope and settings are in the
[replacement protocol](../../docs/STRONG_MATCHED_V2.md).

Exact-byte verified archives: [AES](../aes/strong-smoke-v1/),
[DMA](../dma/strong-smoke-v1/), [Ibex](../ibex/strong-smoke-v1/),
[Mesh](../mesh/strong-smoke-v1/), [RedMulE](../redmule/strong-smoke-v1/).
