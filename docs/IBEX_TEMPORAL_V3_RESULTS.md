# Ibex temporal v3 — context and correction development ablation

All 72 cells completed: four observed development targets × three seeds × six
policies, 16 requested slots each (1,152 total). Read the primary endpoint first:
the base agent has the lowest mean AUC, 5.49% below random descriptively.
Neither source context nor the corrective-feedback package improves the base
agent's mean. This is controller development, not held-out superiority.

## Primary and secondary results

Lower AUC is better. Each policy has 12 cells and 192 slots, including 24 shared
initialization slots. Generated validity below excludes those initialization
slots. Solves use the frozen 0.1 tolerance; unsolved cells remain right-censored
at 16 slots. No failed proposals were repaired or refunded.

| Policy | Mean AUC | Solves / 12 | Generated valid / 168 | Mean behavior cells per run | Estimated USD |
|---|---:|---:|---:|---:|---:|
| Random | 4.831839 | 3 | 156 | 14.33 | 0 |
| Coverage-guided | 5.123888 | 3 | 153 | 7.42 | 0 |
| Base agent | 4.566393 | 3 | 165 | 8.50 | 0.6901 |
| Agent + context | 5.058827 | 2 | 157 | 8.50 | 0.8944 |
| Agent + correction | 5.727038 | 1 | 63 | 4.58 | 0.7856 |
| Agent + both | 5.430726 | 3 | 86 | 4.50 | 1.0036 |

All solves are on the near-flat `target_1`. **No policy solves targets 0, 2 or
3** in this panel. A lower mean AUC does not establish that the agent reaches
more target shapes. Random also visits more cells of the declared behavior
descriptor than any agent. This descriptor measures retirement gaps and dominant
instruction class, not RTL code coverage or the language's expressiveness.

Descriptive paired-package AUC changes (negative favors adding the package):
context without correction +0.492434; context with correction −0.296312;
correction without context +1.160645; correction with context +0.371899.
The interaction is −0.788746. These are descriptive contrasts on three reused
development seeds, not significance tests or independent replications.

## Why the corrective package failed here

The package changed feedback, archive selection and the exploration instruction
together. Its losses cannot be attributed to any one component.

There is a specific output-contract failure. Of 100 schema-rejected correction
slots, 94 contain a nested `program` envelope rather than the required bare
program. Of 78 combined-arm schema failures, 72 have this envelope. A post-hoc
static check finds 83 and 66 of those nested programs, respectively, pass the
program schema. The context-only arm has four such envelopes, all schema-valid
inside. The base arm has none.

For example, `panel/target_0/seed-600/agent-correction/trials.jsonl`, slot 7,
returns `{"program": {...}, "reference_slot": 2}`. The complete inner program
contains registers; the outer candidate does not. Calling all these failures
"missing registers" without inspecting the payload would misdiagnose the issue.
Copying feedback/history structure into the response is a plausible mechanism,
not an established causal explanation. The raw responses are retained.

These checks **do not** establish simulator validity or target quality of rejected
programs. No nested candidate was simulated, unwrapped into the primary ledger,
rescored, or given a replacement slot. The primary results remain unchanged.
There are no PROTOCOL or FUNCTIONAL failures in the panel. Generated USEFUL_WORK
failures are 12 random, 15 coverage, 0 base, 0 context, 5 correction and 4 combined;
each arm also inherits four failed initialization slots. Those are actual
fixed-window completion failures, not schema failures.

## Measurement and provenance

The study was frozen at `dca1344` before calls; the immutable
[protocol](IBEX_TEMPORAL_V3_DEVELOPMENT.md) defines all settings. Both source arms
receive the same eight hashed excerpts (17,538 characters), through a bounded
allowlisted reader. This is supplied context, not autonomous RTL discovery, and
citations are not proof of understanding. The human-written spec is per-design
engineering. Correction feedback uses the identical eight-bin observation window
as the activity evaluator. Retirement gaps are not diagnosed stall causes.

Every arm uses the unchanged 4,096-operation allocator, 200,000-cycle horizon,
common schema, CPU state reference and proposal accounting. Integral encodings
such as `1.0` are canonicalized equally for all arms. The real-CPU gate reproduced
v2 assembly, state, markers and activity. All 192 random slots reproduce the v2
control exactly. Completed v1/v2 studies have not been rewritten.

There were 544 unique cache evaluations, 527 valid, and 336 model calls. Provider
metadata reports `gemini-2.5-flash` throughout: 335 STOP and one MAX_TOKENS finish,
no prompt-feedback block, and no unknown-usage batch. Totals are 4,109,390 input
tokens, 856,329 output tokens including thinking, and estimated **$3.3736395**
at the frozen rates (not an invoice). Each agent run has seven feedback rounds,
not a one-shot proposal. Seeds fix the harness initialization/RNG, not a guarantee
of reproducible cloud-model text; raw outputs and settings are archived.

The measured quantity is fixed-window RTL core activity, **not watts**. No new
GLS power claim follows from this panel. The compact archive audit checks source
hashes, target provenance, reference-state output, interval/count arithmetic,
proposal and token accounting, cached records and aggregates. It is not an
independent rerun of the simulator or raw retirement traces.

## Recommendation

Keep the base controller as the current development candidate. Do not select the
correction package or claim that deeper RTL context improved this controller.
The small base-agent AUC advantage is worth testing, but the unsolved non-flat
targets and lower behavior coverage rule out a claim of broader achieved
temporal expressiveness today. All policies still share one legal language.

Before any further correction experiment, run a separately versioned,
development-only output-contract test: explicitly separate response programs from
history metadata, use the same strict response contract for all agent arms, and
verify complete programs rather than repairing the frozen results. Isolate that
format change from feedback content. Do not assume better compliance will improve
search. Only a subsequently selected, frozen controller should consume fresh
held-out target families and seeds, against both random and coverage baselines.
Those held-out data remain untouched by this study.

## Reviewable evidence

[Complete archive](../results/ibex_temporal_v3_development/README.md),
[aggregate JSON](../results/ibex_temporal_v3_development/aggregate.json), and
[all 72 finalist profiles](../results/ibex_temporal_v3_development/finalists.svg).
Every finalist is shown, including poor ones; no winning examples were selected.

```bash
.venv/bin/python -m analysis.ibex_temporal_v3 \
  --archive results/ibex_temporal_v3_development --verify
```
