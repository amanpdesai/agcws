# Experiment pre-registration

Comparative runs require the endpoint, validity rules, and prompt to be frozen before comparison.

## Primary endpoint

Area under the best-so-far normalized target-error curve versus cumulative evaluator calls. Final error at fixed budget is secondary; wall-clock and dollars are separate.

## Factors and budget

Design: AES, `axi_dma`, Ibex. Goal: scalar, compositional, temporal. Scalar targets: 0.10, 0.25, 0.50, 0.75, 0.90. Policies: random, mutation, evolutionary, expert-GA, one-shot LLM, closed-loop agent, hybrid. Seeds: 10 target, 5 minimum.

Scalar budget is **N=200 proposed candidates** per policy/design/goal/seed. Profile goals use **N=300**. N is provisional until Slice 4 measures activity-evaluator runtime; choose the largest global round number fitting under ten minutes on the slowest design. Every proposal counts, including malformed, schema-invalid, protocol-invalid, and duplicate candidates. LLM batches count per candidate, not per call. Calibration-corpus and SynthesisEvaluator calls are tracked separately.

Log best-so-far error at every index 1..N. Report simulations executed as a secondary budget; the proposal/simulation gap is part of validity reporting.

## Tolerance and calibration

Primary tolerances are ε_s=0.10 normalized envelope units, ε_c=0.05 region-share error, and ε_t=0.10 temporal NRMSE. The initial 0.05 calibration and permitted adjustment are recorded in `DECISIONS.md`; 0.02 and 0.05 remain sensitivity analyses. Scalar q is normalized against each design's non-idle [P_min,P_max].

After Slice 4, on AES only, let r be the median-over-five-seeds fraction of five scalar targets solved by random search within ε_s in ≤20 evaluations. If r>0.6, adjust once to 0.02; if r<0.1, adjust once to 0.10; otherwise retain 0.05. Apply the resulting value globally and record r before comparative runs. If 0.02 still gives r>0.6, G3 fails and profile arms become primary.

Identical workloads must be deterministic across three repeated evaluations. If not, fix nondeterminism; if impossible, set ε≥3× observed run-to-run standard deviation and record it.

Unsolved runs are retained with evaluations-to-target=N (right-censored) and reported alongside solve rate.

## Valid workload definition

- A workload must pass, in order: **SCHEMA → PROTOCOL → FUNCTIONAL → USEFUL WORK**. Failure short-circuits later stages; invalid workloads receive no power score and never enter the scored archive.
- Schema is JSON Schema draft 2020-12, with bounded numeric parameters, known keys/operations, and per-design operation caps.
- Protocol legality is design-specific and pure. Functional validity requires termination, no assertions, no monitored X/Z after reset, and design-specific correctness.
- Slice-4 useful-work floor: AES ≥21 blocks, derived as the floor of the inclusive 10th percentile of the 10-workload valid calibration corpus. The other design floors remain provisional until their corpora exist. The floor is a hard gate, not a penalty.

## Prompt/model freeze

Scalar uses Flash-tier Gemini; compositional/temporal uses Pro-tier Gemini; both tiers run AES scalar as a reportable comparison. Do not guess model versions: record the exact Vertex model identifier on first successful call. Freeze the design-agnostic system prompt at the end of Slice 6 in `prompts/agent_system_v1.txt`, record its SHA-256, and do not tune it per design. Sampling is temperature 0.7, top_p 0.95, max output 4096, batch size 8, strict schema-constrained JSON where supported. Malformed JSON gets at most two reprompts; proposals still count against N.

Use bootstrap CIs, paired nonparametric tests, Holm correction, effect sizes, and a mixed-effects model with policy fixed and design random.
