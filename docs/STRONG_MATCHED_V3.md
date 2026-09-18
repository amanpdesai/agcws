# Strong-model readiness v3 — 2026-09-18

**Smoke completed; operational signoff pending.** Ten calls, zero API errors
or truncations, 16/20 valid generated proposals. The strict per-batch validity
gate fails on AES round one and RedMulE round two. All failures are retained;
the requested operational-readiness exception has not been approved. See the
[complete outcome and measured cost](../results/strong_smoke_v3_plan/README.md).
The full panel remains unlaunched. Do not equate successful transport with a
guarantee of candidate legality, target feasibility or a completed study.

The user approved MEDIUM reasoning with a 65,536-token ceiling. This replaces
the blocked v2 launch candidate, not its evidence. Full matrix execution is
not authorized by the configuration approval.

## Unchanged scientific contract

The [v2 comparison protocol](STRONG_MATCHED_V2.md#frozen-comparison) remains in
force: 450 cells, five designs × nine profiles × ten seeds 9100–9109, 128
proposal slots, two shared initializations, batch two, per-bin absolute
normalized error ≤0.05, early stopping, RMSE best-so-far AUC and the declared
paired inference. CPU baselines and Flash-Lite are reused. No prompt, schema,
target, measurement, legality, or workload modification.

## Explicit v3 changes

- Arm `strong-medium-64k`, model `gemini-3.8-flash`, MEDIUM thinking,
  maximum combined reasoning/answer tokens 65536. Temperature 0.7, top_p 0.95.
- One in-flight provider call across all five sibling design runners, enforced
  by a shared OS file lock in the matrix root. Simulation/cell concurrency is
  unchanged. Queue time is saved separately from provider latency. This avoids
  the previous five-call burst but cannot guarantee absence of provider 429s.
- The launch, checker and accounting support files are hash-pinned in each
  launch contract. Missing/changed code fails closed. Unknown calls retain
  conservative liability; no hidden provider retries or replacement models.

The output allowance and cross-design provider concurrency differ from
Flash-Lite. Report model/configuration and runtime differences, not a pure
model-only causal ablation. API throughput is deliberately conservative for
readiness; any later concurrency change needs a recorded versioned amendment.
Do not delete or replace the global admission lock while any runner is alive.
All design directories must remain siblings under the frozen matrix root.

## Pricing and ceilings

Current verified [Google pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing):
$0.75/M input and $3.75/M output (reasoning included), introductory through
2026-12-31. The ceiling is not automatically billed.

| Illustrative usage | Estimated call cost |
|---|---:|
| 10k input, 20k reasoning/answer | $0.08250 |
| 10k input, all 65536 reasoning/answer | $0.25326 |
| Full admission reservation: 200k input, 65536 output | $0.39576 |

There are at most 28,350 paid calls. The nine accounted v2 smoke calls averaged
$0.0806722, implying $2,287 if all slots are exhausted at that average. This is
not a 64k forecast: early stopping can reduce calls and the larger allowance can
increase usage. At the illustrative 10k/full-output case the matrix is $7,180;
the full reservation bound is $11,219.796. None of these is a Google invoice.

The completed v3 smoke cost estimate is $0.67590675 for ten calls, averaging
$0.067590675. Exhausting every call at that average is $1,916.20. Serial provider
latency extrapolates to 31.7 days if all calls are used at the smoke's mean
latency. Neither extrapolation is a forecast; both make clear that budget and
throughput need a deliberate full-launch decision, not an unconditional promise.

Prepared pause caps stay $120/design ($600 total), not a verified remaining
balance or a promise the panel completes under $600. Full launch needs explicit
authorization and budget acknowledgement. The smoke allows only two provider
calls/design and a $2/design cap, at most ten calls overall.

## Evidence and launch

[Full manifests](../results/strong_matched_v3_plan/README.md) and
[separate smoke](../results/strong_smoke_v3_plan/README.md) are frozen separately.
The smoke uses the same alternating target and seed as v1/v2, six slots with
early stopping disabled so both measured-feedback rounds execute. Every
failure is retained, and no smoke cell is included in paper comparisons.

The readiness audit checks source/runtime equivalence, both rounds' saved
payloads against same-cell history, usage arithmetic, valid measurements,
success/loss arithmetic, completed summaries and restart accounting. It makes
no model calls and performs no missing simulations. Readiness is operational,
not a guarantee every request is feasible or every future call succeeds.

```sh
.venv/bin/python -m maintenance.check_strong_readiness \
  --full out/strong-matched-v3 --smoke out/strong-smoke-v3 \
  --output results/strong_matched_v3_plan/readiness.json
```

Only after this gate passes and the user authorizes launch, run one tmux window
per design, for example:

```sh
.venv/bin/python -u -m maintenance.strong_matrix run \
  --directory out/strong-matched-v3/aes --allow-paid \
  > out/strong-matched-v3/aes/runner.log 2>&1
```

Do not use the bare engine command: it bypasses admission and the audited
accounting wrapper. V1 and v2 are failed, unlaunched candidates; their manifests
and smoke archives remain intact.
