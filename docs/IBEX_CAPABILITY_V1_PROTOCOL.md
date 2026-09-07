# Ibex capability v1 — fixed-context development probe

Declared 2026-09-07 before requests. This is a next-batch capability probe, not
a new held-out search study. Existing v1–v4 protocols/results remain frozen.

## Arms and common information

Four model arms: `gemini-2.5-flash` and `gemini-2.5-pro`, each with thinking budgets
512 and 4,096. The same-generation comparison avoids changing generation and
reasoning-control API together. It does not test every newer/stronger model.
Two CPU controls: random and v3 behavior-coverage, each proposing two programs.

Twelve contexts: all four v4 development targets × seeds 600–602. Take the first
six trials of **v4 base-agent** history in each cell, selected by index, not loss.
Every arm starts with exactly this history. Use the unchanged v4 grounded payload,
including execution diagnostics and prediction notebook, for all four model arms.
No arm receives another arm's new proposals or observations. This deliberately
tests conditional capability under the same information, not on-policy trajectories.

One next batch of two candidates per context/arm: 72 cells, 144 proposed slots;
48 model calls and 24 CPU batches. References must name a valid slot in the
frozen six-trial history; the two new slots cannot reference each other.
CPU controls share history and available diagnostics, with their existing
algorithms deciding what information to use. Seed their proposals deterministically
from the context index and recorded seed, with a separate reproducible RNG per arm.

The model-arm order rotates by context index to balance first/last positions.
Run the first context's four requests serially as an endpoint/settings acceptance
gate, preserving them as study data. If any request fails at the API or has unknown
usage, stop before the remaining requests and record the blocked readiness outcome.
Do not silently switch model, region, schema or retry policy. Local invalidity or
MAX_TOKENS is a measured capability outcome, not authorization to retry.

## Fixed controls and accounting

- The exact v4 workload language, allocator, simulator binary, instrumented
  instruction stream, functional checks and observation window are unchanged.
- Exactly 4,096 semantic operations, 200,000 cycles, eight activity bins; the
  existing target rates, scale 528.45376 and tolerance 0.1 are unchanged.
- Temperature 0.7, top_p 0.95, batch size two, strict JSON with the same relaxed
  native serving schema and unchanged full local validator.
- Common maximum output 16,384 tokens, deliberately above both thinking budgets.
  This differs from v4's 8,192 and is held fixed across this probe, not silently
  compared as a pure v4 model swap. Record actual output and thinking usage.
- One request attempt, 120 s transport deadline, no process/simulation timeout,
  retry or schema repair. Requested slots count on invalid, missing and duplicate
  proposals. Missing prediction metadata is separate from workload validity.
- Record payload/schema hashes, raw text, finish reason, model version, API error,
  usage status, cost, public prediction and observed result before aggregation.
- Freeze source/manifest before calls. Create a durable request-start marker;
  interrupted unknown calls cannot be reissued. Reuse an existing response for
  evaluation recovery only; never sample a replacement response.
- No simultaneous model calls after the acceptance gate (one shared API semaphore),
  at most four supervised context workers. Simulations use `--rm` containers and
  a shared measurement cache; no detached workers or broad container pruning.

Global standard text pricing checked against official pages on 2026-09-07:
Flash $0.30 input / $2.50 output and Pro $1.25 / $10 per million tokens for
inputs up to 200,000 tokens; thinking output is included. Pro long-context rates
are $2.50 / $15. Record token-based estimates, not claimed billing reconciliation.
The frozen payload+schema byte bound plus allowance must fit under 200,000; if
actual provider input exceeds that tier, record the long-context estimate and
flag the assumption rather than undercharging. No tools/grounding charges apply.
Total reservation ceiling $20, checked before requests using conservative input
and maximum-output allowances. Unknown usage retains its reservation liability.

Sources: [pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing),
[thinking controls](https://cloud.google.com/vertex-ai/generative-ai/docs/thinking),
[Pro ID and supported endpoint](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro).
These document support, not this project's actual endpoint access: the frozen
first-context requests establish access. Model versions are reported, not guessed.

## Endpoints and interpretation

Primary: reduction in best temporal error after the two charged proposals,
relative to the best valid candidate in the common historical context. Larger
improvement is better; invalid/unsolved proposals remain and can yield zero gain.
Report all-context mean gain, residual best error, per-target and per-seed means.
This is **not AUC**, a full search solve rate, or held-out superiority.

Secondary: schema/protocol/functional/useful-work validity; context improved;
new tolerance crossings (distinguish contexts already solved); prediction
availability and directional agreement with the ±0.01 neutral band; always-neutral
and class-frequency diagnostics; execution cost, model tokens/dollars and reasons
for termination. Predictions are scored only against visible valid references,
with missingness shown and no removal from the primary denominator.

Report paired differences and the model×budget interaction on common contexts.
Three reused seed units, four related targets and stochastic model requests do
not justify slot-level significance tests or treating 96 model proposals as
independent replications. No significance, equivalence or causal-comprehension
claim. A thinking setting is a maximum resource allowance, not a guarantee of
that many tokens actually used.

For a subsequent depth study, a model arm is a promising development candidate
only if it improves mean gain over Flash-512 by at least 10% (absolute gain if
the control mean is zero), improves at least two of three seed-level means,
has at least 90% workload validity, and has no unknown usage or API errors.
The zero-control rule is strictly positive absolute mean gain; no epsilon is
tuned afterward. This is a screening rule, not a statistical discovery. If none
qualifies, recommend a separate depth/tool investigation, not automatic escalation
to another model. If several qualify, lowest resulting mean error then lowest
estimated cost breaks the tie. Baseline next-batch gains remain visible regardless.

Completion: all declared outcomes (or explicit endpoint-readiness failure), tests,
compact evidence, independent score/payload/provenance audit, report and verified
push. Do not launch a larger search panel, autonomous RTL reader or new design as
an implicit continuation of this probe. Held-out targets/seeds remain untouched.
