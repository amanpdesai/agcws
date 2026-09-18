# Matched Gemini 3.8 panel v2 — prepared, not launched

**NOT READY TO LAUNCH.** [readiness.json](readiness.json) records the Ibex
output-truncation and quota blockers. Configs are frozen candidate inputs, not
approved final-run inputs. Await the user's next model-settings decision.

Explicit arm: `strong-medium-32k`, `gemini-3.8-flash`, MEDIUM thinking,
32768 combined reasoning/output tokens. Five designs × nine profiles × ten
matched seeds = 450 cells. Reuse all CPU and Flash-Lite evidence.

[Protocol](../../docs/STRONG_MATCHED_V2.md) and [preparation.json](preparation.json).
Per-design configs, manifests and launch contracts freeze the tasks, runtime,
model settings and accounting wrapper hashes. Fifty design/seed shared-initial
program checks pass. Only provider registration and its allowlist changed in
the runtime source inventory relative to CPU baselines.

Full launch requires separate user authorization, including the prepared
$120/design ($600 total) pause caps. These are not a cloud balance or assurance
of completion under that cost. V1 is retained but superseded before launch.
