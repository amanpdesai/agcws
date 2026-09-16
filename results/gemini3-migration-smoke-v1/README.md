# Gemini 3 migration smoke — 2026-09-15

Compatibility only, not a comparative study. One AES confirmation-alternating
target, two one-candidate calls per model, MEDIUM thinking, 8192 maximum output
tokens, global Vertex endpoint, google-genai 2.8.0. The second request includes
the first measured workload, rates and signed residuals. Requests remain
stateless with explicit measured history; this does not test conversational
thought-signature circulation. Full provider responses are retained locally.

| Model | Valid simulations | Maximum normalized bin error, call 1 → 2 | Estimated USD |
|---|---:|---:|---:|
| gemini-3.5-flash-lite | 2/2 | 0.227578 → 0.257371 | 0.00653580 |
| gemini-3.8-flash | 2/2 | 0.013465 → 0.000580 | 0.04392075 |

All four calls finished STOP, with no parse failures or provider errors. Both
3.8 proposals pass the every-bin ≤0.05 gate; neither Lite proposal passes.
Total estimated cost, including reasoning tokens: $0.05045655. This tiny,
single-target check supports compatibility, not a model-quality claim.

The script stopped after four calls. It deliberately requested a second proposal
even after success to exercise feedback; this is not the paper early-stop policy.
There were no retries or model substitutions. A local immutable-summary write
error interrupted the script after both Lite calls; saved records were resumed
without repeating either call. A subsequent tuple/list checkpoint comparison
was fixed before any further call. `complete.json`, not the interrupted
`summary.json`, is the authoritative local completion record.

Local evidence: `out/gemini3-migration-smoke-v1/`, including protocol, inputs,
full responses, usage, per-call records and Docker simulation outputs. Runner:
`scripts/smoke_gemini3.py`. These scratch artifacts are not a published study.

All five running/frozen baseline input inventories verified unchanged. New
`.env` ECONOMY_MODEL and STRONG_MODEL keys select these smoke models. The legacy
AGCWS_GEMINI_MODEL and explicit 2.5 study arms remain unchanged: integration and
freezing of Gemini 3 full-study arms is still required before a paid matrix.

Prices used: Lite $0.30/$2.50 and 3.8 $0.75/$3.75 per million input/output tokens,
respectively, including reasoning output. The 3.8 prices are introductory through
2026-12-31: [Google pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing).
