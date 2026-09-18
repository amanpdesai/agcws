# Matched Flash-Lite launch plans

**Historical preparation record.** The subsequent authorized run completed;
see [audited results](../flash_lite_matched_v1/README.md). The frozen files here
remain unchanged, including the original no-execution preparation receipt.

Prepared only, 2026-09-17. **No simulations or paid calls launched.**
Protocol: [FLASH_MATCHED_V1.md](../../docs/FLASH_MATCHED_V1.md).

[readiness.json](readiness.json) records five matched manifests, 450 cells,
the reviewed provider-only source hash differences, and exact equality of all
other source hashes, schemas, runtime identities and task configuration fields.
The baseline reference is each design's published `baselines-model-v1-plan`.
Do not substitute historical `full-flash-v1-plan` configurations.

Model: `gemini-3.5-flash-lite`, MEDIUM thinking, 8192 maximum output tokens.
Each of aes/dma/ibex/mesh/redmule contains the config and frozen manifest.
Execution directories are `out/flash-lite-matched-v1/DESIGN`; no baseline
cache or trials were copied. The Ibex simulator alone was copied and hash-checked.

Nine profiles × ten paired seeds 9100–9109 per design; budget 128, batch two,
early stopping on every-bin absolute normalized error ≤0.05. The already-run
random, GA and model-guided CPU baselines are reused, not executed again.

Preparation verified local ADC availability, configured project and installed
google-genai 2.8.0 without refreshing credentials or calling a model. The earlier
live migration test covers only two AES calls; no claim of new five-design live
provider testing is made. The full frozen matrix is not a guaranteed success
or cost outcome. Proposed pause caps are $120/design and need launch approval.

Verification: **794 tests passed**, three existing warnings, `make lint` clean.
All five `verify_inputs` checks and baseline matching audits pass. The obsolete
transport-only bridge explicitly rejects this model migration; its regression
test remains pinned to the original historical transport change. No new live
model calls, simulations, or result selection occurred during preparation.

The model arm is pinned in code and manifest, not selected from the legacy
`.env` default. Changing `.env` cannot silently replace it. Credentials/project
remain local and are not published here.
