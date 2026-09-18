# Gemini 3.8 MEDIUM/64k compatibility smoke

One alternating target and seed 9100 per design, six slots: two shared initial
programs plus two model batches. Ten API calls maximum, $2/design pause caps.
No early stopping, so the second call sees measured feedback. No replacement
calls for errors and no repair or fallback model.

[Preparation](preparation.json), [protocol](../../docs/STRONG_MATCHED_V3.md),
[failed 8k smoke](../strong_smoke_v1_plan/README.md),
[failed 32k smoke](../strong_smoke_v2_plan/README.md).
All v3 outcomes will be retained; this is not a paper comparison.
