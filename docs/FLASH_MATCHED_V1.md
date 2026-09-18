# Matched Flash-Lite matrix — preparation, not execution

**Completed 2026-09-18:** [audited evidence](../results/flash_lite_matched_v1/README.md).
The preparation text below is retained as the prospective protocol. User
subsequently authorized execution and the documented accounting-only resume;
no target, model, metric or search-budget setting changed.

2026-09-17. The user selected `gemini-3.5-flash-lite`. This supersedes the old
`full-flash-v1-plan` launch files, which contain obsolete measurement targets
and tolerance. Do not launch those files. No paid calls are authorized by this
preparation document.

## Frozen comparison

Copy each published `results/DESIGN/baselines-model-v1-plan/manifest.json` task
contract verbatim, changing only name, policy and proposed cost ceiling.
Five designs × nine profiles × ten seeds **9100–9109** = **450 Flash cells**.
Eight substantive profiles plus one flat control per design; these are observed
targets, not unseen-target confirmation. Reuse the published phase-random,
phase-GA and phase-model evidence, without re-running or altering those arms.

128 charged proposals maximum, two shared initializations, batch two, and early
stop after a batch with **every normalized absolute bin error ≤0.05**. Charge
both siblings and invalid slots. Preserve first-hit index, right-censor failures
at 128, and carry terminal-best RMSE to 128 for AUC. Primary ranking remains
RMSE AUC, not worst-bin AUC. Strict feasibility is unproven for some targets.

Primary reporting: average eight nonflat target AUCs within each paired seed;
ten seed units/design. Compare Flash with each of three CPU arms using paired
seed bootstrap intervals and exact two-sided sign flips, Holm across fifteen
design/arm contrasts. Controls are a separate diagnostic. Report solve rate,
validity, common-valid-evaluation analysis, known USD, unknown liability, runtime
and 16/32/64/128 prefixes. All-target baseline summaries are not substitutes for
the nonflat paired analysis. This is a prospective agent contrast on an already
observed bank, not a new task-held-out claim.

## Model and spending

Explicit arm `flash-lite-medium`: `gemini-3.5-flash-lite`, MEDIUM thinking,
temperature 0.7, top_p 0.95, 8192 total output tokens, global Vertex endpoint,
strict JSON schema, 600-second request deadline, one SDK attempt. No fallback,
candidate repair, web search, code execution, or provider tools. Requests are
stateless with explicit measured history, not conversational continuation.
MEDIUM is not asserted equivalent to the old 4096-token thinking budget.
The prior two-call AES migration smoke established limited live compatibility;
new unit tests check the maintained provider adapter without buying calls.

Pricing checked against [Google's pricing page](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
on 2026-09-17: $0.30 per million input tokens and $2.50 per million output tokens,
including reasoning. Each call reserves $0.08048 at the existing 200,000-input
bound and 8192-output ceiling; unaccounted calls retain liability. At most 63
paid calls/cell, 28,350 overall. The conservative full-bound liability is
$2,281.608, **not a prediction**. Early stops and smaller actual usage reduce it.
Proposed caps remain $120/design ($600 total); these are pause limits, not a
verified cloud balance, guaranteed completion budget, or launch approval.

18 cell workers and one provider worker/design: up to 90 cells and five API
calls concurrently. This preserves the published resource settings. No paid
execution during preparation; the next user authorization should confirm caps.

## Runtime equivalence and launch

Only two runtime files change: model registration/transport settings in
`pipeline/model.py` and the allowed-policy list in `schedule_backend.py`.
The preparation audit requires every other source hash, schema, image and
simulator hash to match the published baseline. Shared initialization equality
is tested for all fifty design/seed pairs. The broad measurement fingerprint
includes model code, so it changes; record this explicitly and never disguise
the new fingerprint as the old one or reuse a baseline measurement cache.

Prepare after committing reviewed provider changes:

```sh
.venv/bin/python -m maintenance.prepare_flash_matrix \
  --directory out/flash-lite-matched-v1 \
  --evidence results/flash_lite_matched_v1_plan
```

Preparation checks inputs and creates manifests only. The receipt is
`results/flash_lite_matched_v1_plan/readiness.json`. After a separate launch
approval, run each design through the existing orchestrator under tmux:

```sh
.venv/bin/python -m agcws.pipeline run \
  --directory out/flash-lite-matched-v1/aes --execute --allow-paid
```

Repeat for dma, ibex, mesh and redmule concurrently, keeping a log per design.
The engine verifies frozen inputs on start/resume and uses atomic cost
reservations. Never delete unresolved request markers to force a retry.
Storage retention remains identical to the completed baseline implementation.
