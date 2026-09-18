# Matched strong-model matrix v2 — 2026-09-18

**Readiness blocked.** V2 produced valid generated workloads on AES (4/4), DMA
(4/4), Mesh (4/4) and RedMulE (3/4). Ibex produced 0/4: its first response hit
MAX_TOKENS and the second received a server-side 429. Do not launch this panel.
See [smoke outcomes](../results/strong_smoke_v2_plan/outcome.json). The next
configuration choice is MEDIUM/65536 versus a separately tested LOW/32768;
neither is applied or frozen. A cross-design provider limiter is also pending,
not claimed implemented. Repeated smokes must not conceal these failures.

Preparation and tiny compatibility smokes are authorized. The full matrix is
not launched. Its explicit model is **gemini-3.8-flash**, arm `strong-medium-32k`:
do not label these prospective results Gemini 2.5 Pro. Earlier Pro studies are
separate evidence, not cells to merge into this panel.

## Frozen comparison

Reuse the published CPU and Flash-Lite panels. Five designs × nine profiles
(eight nonflat, one flat control) × ten seeds 9100–9109 = 450 new agent cells.
The preparer copies the CPU contract and verifies equality of targets, scale,
seed list, simulator/container, workload schema, task settings and shared initial
programs. Only provider registration and its backend allowlist change in the
runtime source inventory. No measurement-cache reuse across fingerprints.

128 charged slots, batch two, two common initial proposals, early stopping on
**every bin's absolute normalized residual ≤0.05**. Invalid proposals consume
slots. RMSE best-so-far AUC remains primary, with terminal-best carryforward to
128 and unsolved runs right-censored. The gate is not per-bin RMSE.

Keep the published analysis: average eight nonflat targets within each seed;
ten seed units/design, paired bootstrap CIs, exact sign flips and Holm over
the fifteen strong-versus-CPU primary contrasts. Strong-versus-Flash-Lite is a
separate five-comparison secondary family. Report all targets and flat controls,
validity stages, solves, budget slices, equal-valid diagnostics, latency and
estimated costs. Do not select a favorable subset after this run.

These targets were observed during development; this is not new-task-held-out
confirmation. Strict 0.05 feasibility is not established for every requested
shape. No single model comparison establishes semantic understanding or a
general power-profile claim: the primary measured quantities remain activity.

## Model and accounting

MEDIUM thinking, 32768 maximum output tokens, temperature 0.7, top_p 0.95,
schema-constrained JSON, global Vertex. The output ceiling differs from the
completed Flash-Lite arm's 8192: this is a model/configuration comparison,
not a pure model-only ablation. Internal reasoning effort is not guaranteed
equal across model families.
The model receives only its own cell's history through the unchanged payload
builder. No web/search tools, witness programs, cross-policy trajectories,
automatic repairs, replacement models or hidden resampling.

Google's [pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing),
checked September 18, lists introductory $0.75/M input and $3.75/M output through
December 31, 2026, including reasoning output. The full request reservation is
$0.27288 (200,000 input + 32768 output). Maximum calls: 28,350; multiplying by
the full reservation gives $7,736.148, a worst-case bound, not a forecast.

Prepared pause caps are $120/design ($600 total), not a verified remaining
balance or a guarantee the matrix finishes without pausing. These caps require
confirmation at full launch. Never equate these estimates with Google billing.

Use `maintenance.strong_matrix` to execute, not the bare engine CLI. It installs
the tested `ReconciledMeter` from the start and verifies frozen wrapper hashes.
For successful responses with known input but incomplete output usage it reserves
the full output ceiling plus observed input; missing reasoning is not zero.
API errors and unresolved requests keep full liability. Every adjustment gets a
hash-linked sidecar; restart does not reset spend or silently repeat a call.

## Readiness and launch

[Preparation manifests](../results/strong_matched_v2_plan/README.md) freeze the
full panel without execution. Separate smokes use one alternating target and
seed per design, six slots (two initial plus two provider batches), no early stop
so feedback is exercised even if the first batch solves. At most ten total API
calls, $2/design caps. They are compatibility checks, excluded from the study.

18 cell workers and one provider worker/design; five design runners can operate
concurrently, up to 90 active cells and five in-flight provider calls. Storage
retention is the already tested compact baseline/Flash path. Checkpoints, locks,
strict input verification and unresolved-call refusal remain unchanged.

After readiness passes and the user authorizes the full launch, start one tmux
window per design with this command, replacing `aes` with the design name:

```sh
.venv/bin/python -u -m maintenance.strong_matrix run \
  --directory out/strong-matched-v2/aes --allow-paid \
  > out/strong-matched-v2/aes/runner.log 2>&1
```

Do not invoke this command during preparation. Review retained errors rather
than relaunching for cleaner smoke outcomes. Any contract change after freeze
requires a new version and equivalence review, not editing the existing files.

## Retained failed configuration

The [v1 smoke](../results/strong_smoke_v1_plan/README.md) had eight MAX_TOKENS
responses in ten calls. Truncated responses spent approximately 7860 thought
tokens, leaving approximately 315 final-response tokens. Google's
[token-limit documentation](https://ai.google.dev/gemini-api/docs/thinking#token-limits-and-max_output_tokens)
confirms the ceiling covers both reasoning and final output. V2 changes only
that ceiling to 32768 and keeps all original records. It is a separately
versioned compatibility correction, not a selective retry or a task change.
The v1 full matrix was never launched and must not be launched.
